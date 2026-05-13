from typing import Dict, Iterable, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from llm_client import LLMConfigError, LLMServiceError, chat_completion, get_llm_identity
from models import AssessmentRecord, Career, CareerPath, UserProfile
from schemas import PlanningChatRequest, PlanningChatResponse


router = APIRouter(prefix="/api/planning", tags=["PlanningAI"])


SYSTEM_PROMPT = (
    "你是面向计算机专业大学生的职业规划顾问。你只回答与计算机专业学习路线、就业、考研、"
    "考公信息化岗位、留学、项目实践、简历面试、职业方向选择有关的问题。必须把系统提供的"
    "个人资料、计算机能力评估、综合能力评估、Career 推荐路径和推荐方向作为唯一事实来源。"
    "没有提供的信息必须明确说“目前资料未提供”，不得编造 GPA、四六级、雅思托福、实习、项目、"
    "城市、经济约束、家庭情况或证书。若用户问题依赖缺失信息，先说明缺失，再给条件化建议。"
    "回答要具体、可执行，避免空话。"
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


def _build_user_prompt(
    profile: UserProfile,
    tech_record: Optional[AssessmentRecord],
    general_record: Optional[AssessmentRecord],
    path_record: Optional[CareerPath],
    careers: List[Career],
    question: str,
) -> str:
    return f"""请严格按以下格式回答：
1. 结论
2. 判断依据
3. 当前短板
4. 1-3 个月行动计划
5. 风险提醒

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
            error="请先完善个人信息后再使用 AI 职业规划问答",
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
        result = chat_completion(messages)
    except (LLMConfigError, LLMServiceError) as exc:
        identity = get_llm_identity()
        return PlanningChatResponse(
            answer="",
            provider=identity["provider"],
            model=identity["model"],
            success=False,
            error=str(exc),
        )

    return PlanningChatResponse(
        answer=result["answer"],
        provider=result["provider"],
        model=result["model"],
        success=True,
        error=None,
    )
