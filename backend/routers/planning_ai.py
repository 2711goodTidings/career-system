import hashlib
import json
import re
from typing import Dict, Iterable, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from llm_client import LLMConfigError, LLMServiceError, chat_completion, get_llm_identity
from models import AssessmentRecord, Career, CareerPath, PlanningYearlyPlanRecord, UserProfile
from schemas import PlanningChatRequest, PlanningChatResponse, PlanningYearlyPlanRequest


router = APIRouter(prefix="/api/planning", tags=["PlanningAI"])


SYSTEM_PROMPT = (
    "你是面向计算机专业大学生的职业规划顾问。你只回答与计算机专业学习路线、就业、考研、"
    "考公信息化岗位、留学、项目实践、简历面试、职业方向选择有关的问题。必须把系统提供的"
    "个人资料、计算机能力评估、综合能力评估、Career 推荐路径和推荐方向作为唯一事实来源。"
    "没有提供的信息必须明确说“目前资料未提供”，不得编造 GPA、四六级、雅思托福、实习、项目、"
    "城市、经济约束、家庭情况或证书。若用户问题依赖缺失信息，先说明缺失，再给条件化建议。"
    "回答要具体、可执行，避免空话。输出使用纯文本，不要使用 Markdown 标题、星号加粗、代码块、表格或项目符号。"
)


GENERAL_DIMENSION_NAMES = {
    "logic": "逻辑思维",
    "innovation": "创新能力",
    "communication": "沟通协作",
    "learning": "学习能力",
    "pressure": "抗压能力",
    "leadership": "领导力",
}


TECH_DIMENSION_NAMES = {
    "programming": "编程能力",
    "algorithm": "数据结构与算法",
    "computer_basic": "计算机基础",
    "software_eng": "软件工程",
    "backend": "后端开发",
    "frontend": "前端开发",
    "database": "数据库",
    "network": "计算机网络",
    "ai_ml": "AI与机器学习",
    "devops": "运维与部署",
}


LEGACY_TECH_DIMENSION_NAMES = {
    "logic": "编程与算法基础",
    "innovation": "工程实践能力",
    "communication": "项目协作表达",
    "learning": "技术学习能力",
    "pressure": "调试与抗压能力",
    "leadership": "技术规划能力",
}


def _safe_text(value: Optional[object], fallback: str = "未提供") -> str:
    text = str(value).strip() if value is not None else ""
    return text or fallback


def _infer_assessment_type(scores: Optional[Dict[str, object]]) -> str:
    score_map = scores if isinstance(scores, dict) else {}
    explicit_type = score_map.get("assessment_type")
    if explicit_type in ["general", "tech"]:
        return explicit_type
    if any(key in score_map for key in TECH_DIMENSION_NAMES):
        return "tech"
    if any(key in score_map for key in GENERAL_DIMENSION_NAMES):
        return "tech"
    return "general"


def _get_latest_assessment_record(
    user_id: int,
    assessment_type: str,
    db: Session,
) -> Optional[AssessmentRecord]:
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )
    for record in records:
        if _infer_assessment_type(record.scores) == assessment_type:
            return record
    return None


def _format_score_lines(scores: Optional[Dict[str, object]], dimensions: Dict[str, str]) -> str:
    if not isinstance(scores, dict) or not scores:
        return "暂无有效能力评估分数"

    lines = []
    for key, label in dimensions.items():
        value = scores.get(key)
        if isinstance(value, (int, float)):
            lines.append(f"- {label}：{float(value):.1f}分")

    return "\n".join(lines) if lines else "暂无有效能力评估分数"


def _format_assessment_record(
    title: str,
    record: Optional[AssessmentRecord],
    dimensions: Dict[str, str],
) -> str:
    if not record or not isinstance(record.scores, dict):
        return f"{title}：暂无记录"

    scores = record.scores
    return f"""{title}：
- 评估等级：{_safe_text(record.overall_level, "暂无")}
- 系统建议：{_safe_text(record.suggestions, "暂无")}
维度得分：
{_format_score_lines(scores, dimensions)}"""


def _format_assessments(
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
) -> str:
    tech_dimensions = TECH_DIMENSION_NAMES
    if tech_record and isinstance(tech_record.scores, dict):
        if not any(key in tech_record.scores for key in TECH_DIMENSION_NAMES):
            tech_dimensions = LEGACY_TECH_DIMENSION_NAMES

    return "\n\n".join(
        [
            _format_assessment_record("计算机能力评估", tech_record, tech_dimensions),
            _format_assessment_record("综合能力评估", general_record, GENERAL_DIMENSION_NAMES),
        ]
    )


def _format_path_record(path_record: Optional[CareerPath]) -> str:
    if not path_record:
        return "暂无 Career 推荐路径记录"

    return f"""- 推荐路径：{_safe_text(path_record.recommend_path, "暂无推荐路径")}
- 路径分析：{_safe_text(path_record.analysis_text, "暂无路径分析")}
- 就业路径评分：{float(path_record.job_score or 0):.1f}
- 考研路径评分：{float(path_record.graduate_score or 0):.1f}
- 考公路径评分：{float(path_record.civil_service_score or 0):.1f}
- 留学路径评分：{float(path_record.abroad_score or 0):.1f}"""


def _format_careers(careers: Iterable[Career]) -> str:
    lines: List[str] = []
    for career in careers:
        detail = "；".join(
            item
            for item in [
                f"方向：{_safe_text(career.career_name)}",
                f"类别：{_safe_text(career.category)}",
                f"技能要求：{_safe_text(career.skill_require)}",
                f"工作/学习内容：{_safe_text(career.work_content)}",
            ]
            if item
        )
        lines.append(f"- {detail}")

    return "\n".join(lines) if lines else "暂无推荐职业方向"


def _assessment_snapshot(record: Optional[AssessmentRecord]) -> Optional[Dict[str, object]]:
    if not record:
        return None
    return {
        "scores": record.scores,
        "overall_level": record.overall_level,
        "suggestions": record.suggestions,
    }


def _build_yearly_plan_input_hash(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    selected_path: str,
    plan_year: str,
) -> str:
    snapshot = {
        "cache_version": "computer_yearly_plan_part_v2",
        "selected_path": selected_path,
        "plan_year": plan_year,
        "profile": {
            "school": profile.school,
            "major": profile.major,
            "grade": profile.grade,
            "interest": profile.interest,
            "skills": profile.skills,
            "target_preference": profile.target_preference,
            "career_goal": profile.career_goal,
        },
        "tech_assessment": _assessment_snapshot(tech_record),
        "general_assessment": _assessment_snapshot(general_record),
        "career_path": None
        if not path_record
        else {
            "job_score": path_record.job_score,
            "graduate_score": path_record.graduate_score,
            "civil_service_score": path_record.civil_service_score,
            "abroad_score": path_record.abroad_score,
            "recommend_path": path_record.recommend_path,
            "analysis_text": path_record.analysis_text,
        },
        "careers": [
            {
                "career_id": career.career_id,
                "career_name": career.career_name,
                "category": career.category,
                "skill_require": career.skill_require,
                "work_content": career.work_content,
                "recommend_path": career.recommend_path,
            }
            for career in careers
        ],
    }
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


ACADEMIC_YEARS = ["大一", "大二", "大三", "大四"]
VALID_PATHS = ["就业", "考研", "考公", "留学"]


def _normalize_grade(grade: Optional[object]) -> Optional[str]:
    text = str(grade or "").strip()
    if not text:
        return None
    alias_map = {
        "大一": ["大一", "一年级", "1年级", "一年", "freshman"],
        "大二": ["大二", "二年级", "2年级", "二年", "sophomore"],
        "大三": ["大三", "三年级", "3年级", "三年", "junior"],
        "大四": ["大四", "四年级", "4年级", "四年", "senior"],
    }
    lower_text = text.lower()
    for year, aliases in alias_map.items():
        if any(alias.lower() in lower_text for alias in aliases):
            return year
    return None


def _remaining_academic_years(grade: Optional[object]) -> List[str]:
    current_year = _normalize_grade(grade)
    if current_year in ACADEMIC_YEARS:
        return ACADEMIC_YEARS[ACADEMIC_YEARS.index(current_year):]
    return ACADEMIC_YEARS


def _plan_part_cache_key(selected_path: str, plan_year: str) -> str:
    path_text = selected_path if selected_path in VALID_PATHS else "推荐"
    return f"{path_text}:{plan_year}"


def _clean_plain_text(answer: str) -> str:
    return (
        str(answer or "")
        .replace("**", "")
        .replace("```", "")
        .replace("`", "")
        .strip()
    )


def _clean_yearly_plan_answer(answer: str) -> str:
    text = _clean_plain_text(answer)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*]\s+", "", text)
    text = re.sub(r"(?m)^\s*-{3,}\s*$", "", text)

    plan_heading = re.search(
        r"(?m)^\s*[一二三四五六七八九十]+[、.．]\s*"
        r"(大一|大二|大三|大四|研一|研二|当前学年|本学年|剩余学年|毕业前|年度|阶段)",
        text,
    )
    if plan_heading:
        text = text[plan_heading.start():]
    else:
        year_heading = re.search(r"(?m)^\s*(大一|大二|大三|大四|研一|研二).{0,12}规划", text)
        if year_heading:
            text = text[year_heading.start():]

    lines = []
    skipping_intro = True
    intro_prefixes = (
        "学生信息",
        "学校：",
        "学校:",
        "年级：",
        "年级:",
        "专业：",
        "专业:",
        "本次规划路径",
        "本次规划路线",
        "路径说明",
        "规划说明",
        "当前判断",
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if skipping_intro and (not line or line.startswith(intro_prefixes)):
            continue
        skipping_intro = False
        lines.append(raw_line.rstrip())

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _build_user_prompt(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    question: str,
) -> str:
    return f"""请严格按以下格式回答，使用纯文本中文小标题，不要使用 Markdown 标题、星号加粗、代码块、表格或 -/* 项目符号：
1. 结论
2. 判断依据
3. 当前短板
4. 1-3 个月行动计划
5. 风险提醒

长度要求：
- 总字数控制在 350 到 500 字。
- 每一部分写 1 到 2 句话，必须完整收尾，不要写到一半中断。
- 如果问题很大，优先回答最关键的判断和下一步，不要铺开长篇解释。

数据使用边界：
- 以下内容来自系统已保存数据；没有列出的内容一律视为“目前资料未提供”。
- 不允许编造用户没有填写的 GPA、排名、四六级、雅思托福、实习、项目数量、城市、经济约束或证书。
- 如果用户目标与 Career 当前推荐路径不同，要说明“用户目标”和“系统推荐”分别基于什么，不要强行覆盖用户目标。
- 如果缺少计算机能力评估，只能给基础建议，不能精确判断具体技术方向匹配度。
- 如果缺少综合能力评估，只能弱化对沟通、抗压、执行力的判断。

用户资料：
- 学校：{_safe_text(profile.school)}
- 年级：{_safe_text(profile.grade)}
- 专业：{_safe_text(profile.major)}
- 兴趣方向：{_safe_text(profile.interest)}
- 已有技能：{_safe_text(profile.skills)}
- 目标倾向：{_safe_text(profile.target_preference)}
- 职业目标：{_safe_text(profile.career_goal)}

能力评估：
{_format_assessments(tech_record, general_record)}

当前 Career 推荐结果：
{_format_path_record(path_record)}

推荐职业方向：
{_format_careers(careers)}

用户提问：
{question}
"""


def _build_yearly_plan_prompt(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    selected_path: Optional[str],
    plan_year: str,
) -> str:
    selected_path_text = _safe_text(selected_path, "未手动选择，默认参考 Career 推荐路径")
    return f"""请只生成“{plan_year}”这一学年的职业成长规划，必须只基于以下系统已保存数据。

输出要求：
- 不要写成问答，不要输出模型说明。
- 输出使用纯文本正文，不要使用 Markdown 标题、星号加粗、代码块、表格或 -/* 项目符号。
- 不要输出总标题、学生信息、学校、年级、专业、本次规划路径、路径说明、数据说明、分隔线或资料摘要。
- 开头必须直接写“{plan_year}年度规划”，不要在它前面加任何解释性段落。
- 只写 {plan_year} 这一年，不要展开其他学年。
- 总字数控制在 400 到 600 字，不能只写一小段，必须完整收尾。
- 必须包含五个小段：年度目标、课程与技术重点、项目或经历、作品与材料产出、风险提醒。
- 每个小段至少写 1 到 2 条具体动作，每条内容不少于 20 个字，必须能落到课程、技术、项目、作品、申请材料或面试准备上。
- 如果学生手动选择的发展路径与 Career 推荐路径不同，要优先尊重“本次选择路径侧重”，同时说明与系统推荐路径的差异。
- 不能编造 GPA、排名、四六级、雅思托福、实习、项目数量、城市、经济约束、证书。
- 语言要具体、可执行，面向计算机专业学生。

当前需要生成的学年：{plan_year}
本次选择路径侧重：{selected_path_text}

用户资料：
- 学校：{_safe_text(profile.school)}
- 年级：{_safe_text(profile.grade)}
- 专业：{_safe_text(profile.major)}
- 兴趣方向：{_safe_text(profile.interest)}
- 已有技能：{_safe_text(profile.skills)}
- 目标倾向：{_safe_text(profile.target_preference)}
- 职业目标：{_safe_text(profile.career_goal)}

能力评估：
{_format_assessments(tech_record, general_record)}

Career 推荐结果：
{_format_path_record(path_record)}

推荐职业方向：
{_format_careers(careers)}
"""


def _build_full_yearly_plan_prompt(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    selected_path: Optional[str],
    plan_years: List[str],
) -> str:
    selected_path_text = _safe_text(selected_path, "未手动选择，默认参考 Career 推荐路径")
    plan_year_text = "、".join(plan_years)
    return f"""请一次性生成“{plan_year_text}”的职业成长规划，必须只基于以下系统已保存数据。

输出要求：
- 不要写成问答，不要输出模型说明。
- 输出使用纯文本正文，不要使用 Markdown 标题、星号加粗、代码块、表格或 -/* 项目符号。
- 不要输出总标题、学生信息、学校、年级、专业、本次规划路径、路径说明、数据说明、分隔线或资料摘要。
- 只生成这些学年：{plan_year_text}，不要增加其他学年。
- 每个学年开头直接写“某某年度规划”，例如“大二年度规划”，学年之间用一个空行分隔。
- 每个学年控制在 220 到 320 字，必须包含：年度目标、课程与技术重点、项目或经历、作品与材料产出、风险提醒。
- 内容要具体、可执行，落到课程、技术、项目、作品、申请材料或面试准备上。
- 如果学生手动选择的发展路径与 Career 推荐路径不同，要优先尊重“本次选择路径侧重”，同时说明与系统推荐路径的差异。
- 不能编造 GPA、排名、四六级、雅思托福、实习、项目数量、城市、经济约束、证书。

当前需要生成的学年：{plan_year_text}
本次选择路径侧重：{selected_path_text}

用户资料：
- 学校：{_safe_text(profile.school)}
- 年级：{_safe_text(profile.grade)}
- 专业：{_safe_text(profile.major)}
- 兴趣方向：{_safe_text(profile.interest)}
- 已有技能：{_safe_text(profile.skills)}
- 目标倾向：{_safe_text(profile.target_preference)}
- 职业目标：{_safe_text(profile.career_goal)}

能力评估：
{_format_assessments(tech_record, general_record)}

Career 推荐结果：
{_format_path_record(path_record)}

推荐职业方向：
{_format_careers(careers)}
"""


def _active_path_label(selected_path: str, path_record: Optional[CareerPath]) -> str:
    if selected_path in VALID_PATHS:
        return selected_path
    if path_record and path_record.recommend_path:
        return str(path_record.recommend_path)
    return "就业"


def _career_name_text(careers: List[Career]) -> str:
    names = [career.career_name for career in careers if career.career_name]
    return "、".join(names[:3]) if names else "后端、前端、AI、数据等计算机方向"


def _build_rule_based_chat_answer(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    question: str,
) -> str:
    path_text = _active_path_label("", path_record)
    career_text = _career_name_text(careers)
    assessment_note = "已参考最新能力评估" if tech_record or general_record else "当前缺少能力评估，建议会偏基础"

    return f"""1. 结论
AI 服务暂时没有完成响应，先按系统已保存资料给你一版本地建议。你当前可以围绕{path_text}路径推进，优先参考{career_text}。

2. 判断依据
本次只使用你的年级、专业、兴趣、已有技能、目标倾向、Career 推荐结果与能力评估记录；没有填写的信息不参与判断。{assessment_note}，后续补齐资料后判断会更准。

3. 当前短板
如果目标还不清晰，先不要同时铺太多方向；用一个主攻技术方向、一段可展示项目和一份持续更新的材料包，把能力证据沉淀下来。

4. 1-3 个月行动计划
选择一个与目标路径贴近的小项目，完成需求、实现、部署或复盘文档；同步整理简历、作品说明和面试题清单。针对你的问题“{question[:60]}”，先拆成本周能完成的一个动作。

5. 风险提醒
资料不足或路径频繁切换时，规划容易变泛；建议先完成个人资料、综合能力评估和计算机能力评估，再让 AI 服务恢复后生成更细版本。"""


def _build_rule_based_yearly_plan(
    profile: UserProfile,
    path_text: str,
    careers: List[Career],
    plan_years: List[str],
) -> str:
    career_text = _career_name_text(careers)
    path_focus = {
        "就业": "实习、项目作品、简历和面试准备",
        "考研": "数学、专业课、英语、复试材料和科研/项目经历",
        "考公": "行测申论、计算机基础、信息化岗位认知和材料表达",
        "留学": "语言考试、课程成绩、项目/科研经历和申请文书",
    }.get(path_text, "课程基础、项目作品、材料整理和阶段复盘")

    year_focus = {
        "大一": "夯实编程、计算机基础和学习习惯，先做小而完整的课程项目。",
        "大二": "确定主攻方向，补强数据结构、数据库、前后端或 AI 基础，并形成可展示作品。",
        "大三": "围绕目标路径强化项目、实习、竞赛、科研或考试准备，沉淀可证明材料。",
        "大四": "完成求职、升学、考公或申请冲刺，打磨简历、作品集、文书和面试表达。",
    }

    parts = []
    for plan_year in plan_years:
        focus = year_focus.get(plan_year, "围绕目标路径安排课程、项目和材料产出。")
        parts.append(
            f"""{plan_year}年度规划
年度目标：围绕{path_text}路径建立清晰主线，重点放在{path_focus}。结合当前专业、兴趣和技能情况，先把目标压缩到 1 个主方向，参考{career_text}持续校准。
课程与技术重点：{focus}每周固定复盘一次课程、技术栈和薄弱点，把学习记录转化为可检查的任务。
项目或经历：至少推进一个能展示能力的项目或经历，保留需求、实现过程、问题解决和结果截图，避免只有零散练习。
作品与材料产出：维护简历、作品说明、项目仓库或申请材料，把课程基础、技术能力和阶段成果串成证据链。
风险提醒：不要编造未填写的成绩、证书、实习或项目数量；资料不足时先补齐个人信息和能力评估，再细化下一轮计划。"""
        )

    return "\n\n".join(parts)


@router.post("/chat", response_model=PlanningChatResponse)
def planning_chat(payload: PlanningChatRequest, db: Session = Depends(get_db)):
    question = payload.question.strip()
    identity = get_llm_identity()

    if not question:
        return PlanningChatResponse(
            answer="",
            provider=identity["provider"],
            model=identity["model"],
            success=False,
            error="请输入要咨询的问题",
        )

    profile = db.query(UserProfile).filter(UserProfile.user_id == payload.user_id).first()
    if not profile:
        return PlanningChatResponse(
            answer="",
            provider=identity["provider"],
            model=identity["model"],
            success=False,
            error="请先完善个人信息后再使用规划咨询",
        )

    tech_record = _get_latest_assessment_record(payload.user_id, "tech", db)
    general_record = _get_latest_assessment_record(payload.user_id, "general", db)
    path_record = db.query(CareerPath).filter(CareerPath.user_id == payload.user_id).first()

    careers_query = db.query(Career).filter(Career.is_active == True)
    if path_record and path_record.recommend_path:
        careers_query = careers_query.filter(Career.recommend_path == path_record.recommend_path)
    careers = careers_query.limit(3).all()
    if not careers:
        careers = db.query(Career).filter(Career.is_active == True).limit(3).all()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _build_user_prompt(profile, tech_record, general_record, path_record, careers, question),
        },
    ]

    try:
        result = chat_completion(messages, max_tokens=1400)
    except (LLMConfigError, LLMServiceError) as exc:
        fallback_answer = _build_rule_based_chat_answer(
            profile,
            tech_record,
            general_record,
            path_record,
            careers,
            question,
        )
        return PlanningChatResponse(
            answer=fallback_answer,
            provider="local",
            model="rule-fallback",
            success=True,
            error=str(exc),
        )

    answer = str(result["answer"]).strip()
    if not answer:
        answer = _build_rule_based_chat_answer(
            profile,
            tech_record,
            general_record,
            path_record,
            careers,
            question,
        )
        return PlanningChatResponse(
            answer=answer,
            provider="local",
            model="rule-fallback",
            success=True,
            error="AI 服务返回了空内容，已切换为本地规则建议",
        )

    return PlanningChatResponse(
        answer=answer,
        provider=result["provider"],
        model=result["model"],
        success=True,
        error=None,
    )


@router.post("/yearly-plan", response_model=PlanningChatResponse)
def planning_yearly_plan(payload: PlanningYearlyPlanRequest, db: Session = Depends(get_db)):
    identity = get_llm_identity()
    profile = db.query(UserProfile).filter(UserProfile.user_id == payload.user_id).first()
    if not profile:
        return PlanningChatResponse(
            answer="",
            provider=identity["provider"],
            model=identity["model"],
            success=False,
            error="请先完善个人信息后再生成职业成长规划书",
        )

    tech_record = _get_latest_assessment_record(payload.user_id, "tech", db)
    general_record = _get_latest_assessment_record(payload.user_id, "general", db)
    path_record = db.query(CareerPath).filter(CareerPath.user_id == payload.user_id).first()

    careers_query = db.query(Career).filter(Career.is_active == True)
    selected_path = (payload.selected_path or "").strip()
    if selected_path in VALID_PATHS:
        careers_query = careers_query.filter(Career.recommend_path == selected_path)
    elif path_record and path_record.recommend_path:
        careers_query = careers_query.filter(Career.recommend_path == path_record.recommend_path)
    careers = careers_query.limit(3).all()
    if not careers:
        careers = db.query(Career).filter(Career.is_active == True).limit(3).all()

    plan_years = _remaining_academic_years(profile.grade)
    cache_key = _plan_part_cache_key(selected_path, "完整规划")
    input_hash = _build_yearly_plan_input_hash(
        profile,
        tech_record,
        general_record,
        path_record,
        careers,
        selected_path,
        "full:" + "|".join(plan_years),
    )

    cached_record = (
        db.query(PlanningYearlyPlanRecord)
        .filter(
            PlanningYearlyPlanRecord.user_id == payload.user_id,
            PlanningYearlyPlanRecord.selected_path == cache_key,
            PlanningYearlyPlanRecord.input_hash == input_hash,
        )
        .order_by(PlanningYearlyPlanRecord.created_at.desc())
        .first()
    )
    if cached_record:
        return PlanningChatResponse(
            answer=_clean_yearly_plan_answer(cached_record.answer),
            provider=cached_record.provider or identity["provider"],
            model=cached_record.model or identity["model"],
            success=True,
            error=None,
            from_cache=True,
            created_at=cached_record.created_at,
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _build_full_yearly_plan_prompt(
                profile,
                tech_record,
                general_record,
                path_record,
                careers,
                selected_path,
                plan_years,
            ),
        },
    ]

    try:
        result = chat_completion(messages, max_tokens=2600)
    except (LLMConfigError, LLMServiceError) as exc:
        fallback_answer = _build_rule_based_yearly_plan(
            profile,
            _active_path_label(selected_path, path_record),
            careers,
            plan_years,
        )
        return PlanningChatResponse(
            answer=fallback_answer,
            provider="local",
            model="rule-fallback",
            success=True,
            error=str(exc),
            from_cache=False,
        )

    clean_answer = _clean_yearly_plan_answer(result["answer"])
    if not clean_answer:
        fallback_answer = _build_rule_based_yearly_plan(
            profile,
            _active_path_label(selected_path, path_record),
            careers,
            plan_years,
        )
        return PlanningChatResponse(
            answer=fallback_answer,
            provider="local",
            model="rule-fallback",
            success=True,
            error="AI 服务返回了空内容，已切换为本地规则规划",
            from_cache=False,
        )

    try:
        plan_record = PlanningYearlyPlanRecord(
            user_id=payload.user_id,
            selected_path=cache_key,
            input_hash=input_hash,
            answer=clean_answer,
            provider=result["provider"],
            model=result["model"],
        )
        db.add(plan_record)
        db.commit()
        db.refresh(plan_record)
        created_at = plan_record.created_at
    except Exception as exc:
        db.rollback()
        return PlanningChatResponse(
            answer=clean_answer,
            provider=result["provider"],
            model=result["model"],
            success=True,
            error=f"规划已生成，但历史记录保存失败：{exc}",
            from_cache=False,
        )

    return PlanningChatResponse(
        answer=clean_answer,
        provider=result["provider"],
        model=result["model"],
        success=True,
        error=None,
        from_cache=False,
        created_at=created_at,
    )
