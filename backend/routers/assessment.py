import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from llm_client import LLMConfigError, LLMServiceError, chat_completion
from models import AssessmentQuestion, AssessmentRecord, User, UserProfile

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

GENERAL_DIMENSIONS = {
    "logic": "逻辑思维",
    "innovation": "创新能力",
    "communication": "沟通协作",
    "learning": "学习能力",
    "pressure": "抗压能力",
    "leadership": "领导力",
}

TECH_DIMENSIONS = {
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

DIMENSION_NAMES = {
    **GENERAL_DIMENSIONS,
    **TECH_DIMENSIONS,
}

ASSESSMENT_TYPE_LABELS = {
    "general": "综合能力评估",
    "tech": "计算机能力评估",
}

DEFAULT_QUESTIONS = [
    {"dimension": "logic", "question_text": "我能够快速理解复杂的概念和问题。", "order_num": 1},
    {"dimension": "logic", "question_text": "我喜欢分析和解决需要推理的问题。", "order_num": 2},
    {"dimension": "logic", "question_text": "我能够从多个角度思考同一个问题。", "order_num": 3},
    {"dimension": "innovation", "question_text": "我经常能想到别人想不到的点子。", "order_num": 4},
    {"dimension": "innovation", "question_text": "我喜欢尝试新的方法和思路。", "order_num": 5},
    {"dimension": "innovation", "question_text": "面对问题时，我愿意寻找不同的解决方案。", "order_num": 6},
    {"dimension": "communication", "question_text": "我能够清晰地表达自己的想法。", "order_num": 7},
    {"dimension": "communication", "question_text": "我善于倾听他人的意见。", "order_num": 8},
    {"dimension": "communication", "question_text": "我在团队中能够较好地与他人合作。", "order_num": 9},
    {"dimension": "learning", "question_text": "我学习新知识的速度比较快。", "order_num": 10},
    {"dimension": "learning", "question_text": "我能够主动寻找学习资源。", "order_num": 11},
    {"dimension": "learning", "question_text": "我善于总结和归纳学到的知识。", "order_num": 12},
    {"dimension": "pressure", "question_text": "面对压力时我能保持冷静。", "order_num": 13},
    {"dimension": "pressure", "question_text": "我能够较好地应对突发状况。", "order_num": 14},
    {"dimension": "pressure", "question_text": "失败后我能够较快调整心态。", "order_num": 15},
    {"dimension": "leadership", "question_text": "我能够影响和带动身边的人。", "order_num": 16},
    {"dimension": "leadership", "question_text": "我愿意承担责任。", "order_num": 17},
    {"dimension": "leadership", "question_text": "我能够协调团队资源达成目标。", "order_num": 18},
    {"dimension": "programming", "question_text": "我能熟练使用至少一门编程语言（Python/Java/Go/C++）进行开发。", "order_num": 19},
    {"dimension": "programming", "question_text": "我理解面向对象编程的核心概念（封装、继承、多态）。", "order_num": 20},
    {"dimension": "programming", "question_text": "我熟悉函数式编程的基本概念和常用操作。", "order_num": 21},
    {"dimension": "algorithm", "question_text": "我熟练掌握常用数据结构（数组、链表、栈、队列、哈希表、树、图）。", "order_num": 22},
    {"dimension": "algorithm", "question_text": "我能解决中等难度的算法题（LeetCode 中等题）。", "order_num": 23},
    {"dimension": "algorithm", "question_text": "我理解时间复杂度和空间复杂度的分析方法。", "order_num": 24},
    {"dimension": "computer_basic", "question_text": "我理解操作系统的基本概念（进程、线程、内存管理、文件系统）。", "order_num": 25},
    {"dimension": "computer_basic", "question_text": "我熟悉计算机网络核心协议（TCP/IP、HTTP/HTTPS、DNS）。", "order_num": 26},
    {"dimension": "computer_basic", "question_text": "我了解计算机组成原理（CPU、内存、I/O、指令集）。", "order_num": 27},
    {"dimension": "software_eng", "question_text": "我能熟练使用 Git 进行版本控制和团队协作。", "order_num": 28},
    {"dimension": "software_eng", "question_text": "我了解软件开发生命周期和敏捷开发流程。", "order_num": 29},
    {"dimension": "software_eng", "question_text": "我能够编写单元测试和集成测试。", "order_num": 30},
    {"dimension": "backend", "question_text": "我能使用框架（Spring Boot/Django/Express 等）开发后端应用。", "order_num": 31},
    {"dimension": "backend", "question_text": "我理解 RESTful API 设计和数据库交互。", "order_num": 32},
    {"dimension": "backend", "question_text": "我了解微服务架构和消息队列的基本概念。", "order_num": 33},
    {"dimension": "frontend", "question_text": "我能使用框架（React/Vue/Angular）开发前端页面。", "order_num": 34},
    {"dimension": "frontend", "question_text": "我掌握 HTML5/CSS3/JavaScript/TypeScript。", "order_num": 35},
    {"dimension": "frontend", "question_text": "我了解前端工程化（Webpack/Vite、状态管理、路由）。", "order_num": 36},
    {"dimension": "database", "question_text": "我能编写复杂的 SQL 查询，理解索引和事务。", "order_num": 37},
    {"dimension": "database", "question_text": "我了解至少一种 NoSQL 数据库（Redis/MongoDB）。", "order_num": 38},
    {"dimension": "database", "question_text": "我了解数据库设计和范式理论。", "order_num": 39},
    {"dimension": "network", "question_text": "我理解 HTTP 协议细节、状态码和常见 Web 安全问题。", "order_num": 40},
    {"dimension": "network", "question_text": "我了解负载均衡、CDN、DNS 解析原理。", "order_num": 41},
    {"dimension": "network", "question_text": "我熟悉 TCP 三次握手、四次挥手和拥塞控制。", "order_num": 42},
    {"dimension": "ai_ml", "question_text": "我了解机器学习的基本概念（监督/无监督学习、分类/回归）。", "order_num": 43},
    {"dimension": "ai_ml", "question_text": "我使用过至少一种深度学习框架（PyTorch/TensorFlow）。", "order_num": 44},
    {"dimension": "ai_ml", "question_text": "我了解大语言模型的基本原理和应用场景。", "order_num": 45},
    {"dimension": "devops", "question_text": "我熟悉 Linux 常用命令和 Shell 脚本编写。", "order_num": 46},
    {"dimension": "devops", "question_text": "我了解 Docker 容器化和 CI/CD 流程。", "order_num": 47},
    {"dimension": "devops", "question_text": "我了解云服务（阿里云/腾讯云/AWS）的基本使用。", "order_num": 48},
]


def normalize_assessment_type(value: str | None) -> str:
    return value if value in ASSESSMENT_TYPE_LABELS else "tech"


def dimensions_for_type(assessment_type: str) -> Dict[str, str]:
    return GENERAL_DIMENSIONS if assessment_type == "general" else TECH_DIMENSIONS


def question_type(question: AssessmentQuestion) -> str:
    return "general" if question.dimension in GENERAL_DIMENSIONS else "tech"


def build_rule_based_suggestion(
    assessment_type: str,
    raw_scores: Dict[str, float],
    strongest: tuple,
    weakest: tuple,
    user_id: Optional[int],
    db: Session,
) -> str:
    label = ASSESSMENT_TYPE_LABELS[assessment_type]
    suggestions = (
        f"【{label}】你的{DIMENSION_NAMES[strongest[0]]}较突出（{strongest[1]:.0f}分），"
        f"{DIMENSION_NAMES[weakest[0]]}还有提升空间（{weakest[1]:.0f}分）。"
    )

    if assessment_type == "tech":
        return suggestions + build_tech_suggestion(raw_scores, weakest[0])
    return suggestions + build_general_suggestion(raw_scores, weakest[0], user_id, db)


def build_ai_assessment_prompt(
    assessment_type: str,
    raw_scores: Dict[str, float],
    overall_level: str,
    strongest: tuple,
    weakest: tuple,
    user_id: Optional[int],
    db: Session,
) -> str:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first() if user_id else None
    dimensions = dimensions_for_type(assessment_type)
    score_lines = "\n".join(
        f"- {dimensions.get(key, key)}：{score:.1f}分"
        for key, score in raw_scores.items()
        if key in dimensions
    )
    role = "职业规划导师" if assessment_type == "general" else "计算机专业技术成长导师"
    task_name = ASSESSMENT_TYPE_LABELS[assessment_type]

    return f"""你是{role}，请基于学生真实评估结果生成一段中文建议。

硬性要求：
- 只使用下面提供的信息，不要编造 GPA、四六级、实习、项目数量、证书或城市。
- 建议控制在 120 到 160 字，不要只给一句笼统结论。
- 结构包含：能力分析、提升重点、下一步行动。
- 直接输出最终建议，不要寒暄，不要解释生成过程。
- 输出使用纯文本，不要使用 Markdown 标题、星号加粗、代码块、表格或 -/* 项目符号。
- 语气专业、具体、可执行，不要泛泛鼓励。

评估类型：{task_name}
综合等级：{overall_level}
最强维度：{dimensions.get(strongest[0], strongest[0])}（{strongest[1]:.0f}分）
待提升维度：{dimensions.get(weakest[0], weakest[0])}（{weakest[1]:.0f}分）

维度得分：
{score_lines}

学生资料：
- 年级：{profile.grade if profile and profile.grade else "未填写"}
- 专业：{profile.major if profile and profile.major else "未填写"}
- 兴趣方向：{profile.interest if profile and profile.interest else "未填写"}
- 已有技能：{profile.skills if profile and profile.skills else "未填写"}
- 目标倾向：{profile.target_preference if profile and profile.target_preference else "未填写"}
- 职业目标：{profile.career_goal if profile and profile.career_goal else "未填写"}
"""


def build_ai_suggestion(
    assessment_type: str,
    raw_scores: Dict[str, float],
    overall_level: str,
    strongest: tuple,
    weakest: tuple,
    user_id: Optional[int],
    db: Session,
) -> Tuple[Optional[str], str]:
    prompt = build_ai_assessment_prompt(assessment_type, raw_scores, overall_level, strongest, weakest, user_id, db)
    try:
        result = chat_completion(
            [
                {
                    "role": "system",
                    "content": "你是专业的计算机专业职业规划助手，必须严格依据用户已提供的数据生成建议，输出纯文本，不要使用 Markdown。",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=360,
            timeout_seconds=60,
            retry_attempts=3,
        )
    except (LLMConfigError, LLMServiceError) as exc:
        return None, str(exc)

    answer = (result.get("answer") or "").strip()
    return (answer, "") if answer else (None, "AI 服务返回了空内容")


def build_assessment_suggestion(
    assessment_type: str,
    raw_scores: Dict[str, float],
    overall_level: str,
    strongest: tuple,
    weakest: tuple,
    user_id: Optional[int],
    db: Session,
) -> Tuple[str, str, str]:
    ai_suggestion, ai_error = build_ai_suggestion(assessment_type, raw_scores, overall_level, strongest, weakest, user_id, db)
    if ai_suggestion:
        return ai_suggestion, "ai", ""
    return "AI 建议暂未生成成功，请稍后重新提交评估重试。", "ai_error", ai_error


def normalize_answer_signature(answers: Dict[str, int]) -> Dict[str, int]:
    return {str(key): int(value) for key, value in sorted(answers.items(), key=lambda item: int(item[0]))}


def get_cached_assessment_suggestion(
    user_id: Optional[int],
    assessment_type: str,
    clean_answers: Dict[str, int],
    db: Session,
) -> Optional[Tuple[str, str]]:
    if not user_id or not clean_answers:
        return None

    current_signature = normalize_answer_signature(clean_answers)
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )

    for record in records:
        scores = record.scores if isinstance(record.scores, dict) else {}
        if scores.get("assessment_type") != assessment_type:
            continue
        if scores.get("suggestion_source") not in {"ai", "history_ai"}:
            continue

        saved_answers = record.answers if isinstance(record.answers, dict) else {}
        if normalize_answer_signature(saved_answers) == current_signature and record.suggestions:
            return record.suggestions, "history_ai"

    return None


@router.on_event("startup")
async def init_questions():
    db = SessionLocal()
    try:
        current_questions = db.query(AssessmentQuestion).order_by(AssessmentQuestion.order_num).all()
        current_snapshot = [
            {
                "dimension": question.dimension,
                "question_text": question.question_text,
                "order_num": question.order_num,
            }
            for question in current_questions
        ]
        if current_snapshot != DEFAULT_QUESTIONS:
            db.query(AssessmentQuestion).delete()
            for question_data in DEFAULT_QUESTIONS:
                db.add(AssessmentQuestion(**question_data))
            db.commit()
            print(f"Initialized assessment questions: {len(DEFAULT_QUESTIONS)} total.")
    except Exception as exc:
        db.rollback()
        print(f"Failed to initialize assessment questions: {exc}")
    finally:
        db.close()


@router.get("/questions")
def get_questions(
    assessment_type: str = Query("tech", alias="type"),
    db: Session = Depends(get_db),
):
    normalized_type = normalize_assessment_type(assessment_type)
    allowed_dimensions = set(dimensions_for_type(normalized_type))
    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.dimension.in_(allowed_dimensions))
        .order_by(AssessmentQuestion.order_num)
        .all()
    )
    return [
        {
            "id": q.id,
            "dimension": q.dimension,
            "question_text": q.question_text,
            "order_num": q.order_num,
            "assessment_type": normalized_type,
        }
        for q in questions
    ]


@router.post("/submit")
def submit_assessment(submit_data: Dict[str, Any], db: Session = Depends(get_db)):
    answers = submit_data.get("answers") or {}
    user_id: Optional[int] = submit_data.get("user_id")
    assessment_type = normalize_assessment_type(submit_data.get("assessment_type") or submit_data.get("type"))

    if user_id is not None:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在，无法保存能力评估结果")

    allowed_dimensions = dimensions_for_type(assessment_type)
    questions = (
        db.query(AssessmentQuestion)
        .filter(AssessmentQuestion.dimension.in_(set(allowed_dimensions)))
        .all()
    )
    question_map = {q.id: q for q in questions}

    dimension_scores: Dict[str, List[int]] = {dimension: [] for dimension in allowed_dimensions}
    clean_answers: Dict[str, int] = {}
    for question_id, score in answers.items():
        try:
            q_id = int(question_id)
            value = int(score)
        except (TypeError, ValueError):
            continue

        if q_id in question_map and 1 <= value <= 5:
            clean_answers[str(q_id)] = value
            dimension_scores[question_map[q_id].dimension].append(value)

    raw_scores: Dict[str, float] = {}
    for dimension, scores in dimension_scores.items():
        raw_scores[dimension] = round((sum(scores) / len(scores) / 5) * 100, 2) if scores else 50.0

    avg_score = sum(raw_scores.values()) / len(raw_scores)
    if avg_score >= 85:
        overall_level = "优秀"
    elif avg_score >= 70:
        overall_level = "良好"
    elif avg_score >= 55:
        overall_level = "中等"
    else:
        overall_level = "待提升"

    strongest = max(raw_scores.items(), key=lambda item: item[1])
    weakest = min(raw_scores.items(), key=lambda item: item[1])
    cached_suggestion = get_cached_assessment_suggestion(user_id, assessment_type, clean_answers, db)
    if cached_suggestion:
        suggestions, suggestion_source = cached_suggestion
        suggestion_error = ""
    else:
        suggestions, suggestion_source, suggestion_error = build_assessment_suggestion(
            assessment_type,
            raw_scores,
            overall_level,
            strongest,
            weakest,
            user_id,
            db,
        )

    saved_scores = {
        **raw_scores,
        "assessment_type": assessment_type,
        "suggestion_source": suggestion_source,
        "suggestion_error": suggestion_error,
    }
    record = AssessmentRecord(
        user_id=user_id,
        scores=saved_scores,
        answers=clean_answers,
        overall_level=overall_level,
        suggestions=suggestions,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "scores": raw_scores,
        "overall_level": overall_level,
        "suggestions": suggestions,
        "radar_data": raw_scores,
        "assessment_type": assessment_type,
        "suggestion_source": suggestion_source,
        "suggestion_error": suggestion_error,
        "created_at": record.created_at.isoformat(),
    }


def build_tech_suggestion(scores: Dict[str, float], weakest_key: str) -> str:
    tech_avg = sum(scores.values()) / len(scores)
    if tech_avg >= 80:
        text = f"\n\n【计算机能力】整体优秀（{tech_avg:.0f}分），可以开始围绕目标岗位做项目深挖和面试表达。"
    elif tech_avg >= 60:
        text = f"\n\n【计算机能力】基础可用（{tech_avg:.0f}分），建议选择一个主方向，把项目和基础课串起来。"
    else:
        text = f"\n\n【计算机能力】仍需系统补强（{tech_avg:.0f}分），建议先补编程、算法和计算机基础。"

    action_map = {
        "programming": "选择一门主语言，完成一个包含文件/接口/数据库的小项目。",
        "algorithm": "从数组、链表、哈希表、树、图和动态规划高频题开始，每周固定刷题。",
        "computer_basic": "补操作系统、计算机网络、数据库和组成原理，形成面试笔记。",
        "software_eng": "练习 Git 协作、测试、代码规范和需求拆解，把项目做成可维护版本。",
        "backend": "用 Spring Boot/FastAPI/Express 完成接口、鉴权、日志和数据库模块。",
        "frontend": "用 Vue/React 完成组件化页面、路由、状态管理和接口联调。",
        "database": "练习 SQL、索引、事务、表设计和 Redis/MongoDB 基础场景。",
        "network": "补 HTTP、TCP/IP、DNS、CDN、负载均衡和常见 Web 安全问题。",
        "ai_ml": "用 Python 完成数据处理、模型调用或机器学习小项目。",
        "devops": "练习 Linux、Docker、CI/CD 和云服务部署，把项目真正跑起来。",
    }
    return text + f"\n重点补强：{action_map.get(weakest_key, '围绕最低分维度制定 3-6 个月专项计划。')}"


def build_general_suggestion(scores: Dict[str, float], weakest_key: str, user_id: Optional[int], db: Session) -> str:
    text = "\n\n【综合能力】这部分用于辅助判断学习节奏、表达协作和长期执行，不会直接替代计算机技能评估。"
    action_map = {
        "logic": "多做结构化分析训练，把问题拆成条件、约束、步骤和结论。",
        "innovation": "尝试给课程项目增加不同方案、交互设计或业务场景。",
        "communication": "用 STAR 结构练习讲项目，补充 README、汇报材料和答辩表达。",
        "learning": "建立固定输入、练习、输出、复盘的学习闭环。",
        "pressure": "记录压力场景下的错误、原因、处理方式和复盘动作。",
        "leadership": "把目标拆成周任务，明确优先级、验收标准和复盘节奏。",
    }
    if user_id:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile and profile.interest:
            text += f"\n结合你填写的兴趣「{profile.interest}」，建议把优势能力迁移到项目展示和职业表达里。"
    return text + f"\n重点补强：{action_map.get(weakest_key, '选择最低分维度制定专项提升计划。')}"


@router.get("/history/{user_id}")
def get_assessment_history(
    user_id: int,
    assessment_type: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_db),
):
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )
    normalized_type = normalize_assessment_type(assessment_type) if assessment_type else None
    result = []
    for record in records:
        scores = record.scores if isinstance(record.scores, dict) else {}
        record_type = scores.get("assessment_type") or infer_record_type(scores)
        if normalized_type and record_type != normalized_type:
            continue
        clean_scores = {key: value for key, value in scores.items() if key in DIMENSION_NAMES}
        result.append(
            {
                "id": record.id,
                "scores": clean_scores,
                "overall_level": record.overall_level,
                "assessment_type": record_type,
                "created_at": record.created_at.isoformat(),
            }
        )
    return result


def infer_record_type(scores: Dict[str, Any]) -> str:
    if any(key in scores for key in TECH_DIMENSIONS):
        return "tech"
    return "general"
