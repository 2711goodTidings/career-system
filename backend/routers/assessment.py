import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from models import AssessmentQuestion, AssessmentRecord, User

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

DIMENSION_NAMES = {
    "logic": "逻辑思维",
    "innovation": "创新能力",
    "communication": "沟通协作",
    "learning": "学习能力",
    "pressure": "抗压能力",
    "leadership": "领导力",
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
]


@router.on_event("startup")
async def init_questions():
    db = SessionLocal()
    try:
        dimensions = {row[0] for row in db.query(AssessmentQuestion.dimension).distinct().all()}
        expected = set(DIMENSION_NAMES)
        if dimensions != expected:
            db.query(AssessmentQuestion).delete()
            for question_data in DEFAULT_QUESTIONS:
                db.add(AssessmentQuestion(**question_data))
            db.commit()
            print("Initialized assessment questions with 6 assessment dimensions.")
    except Exception as exc:
        db.rollback()
        print(f"Failed to initialize assessment questions: {exc}")
    finally:
        db.close()


@router.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(AssessmentQuestion).order_by(AssessmentQuestion.order_num).all()
    return [
        {
            "id": q.id,
            "dimension": q.dimension,
            "question_text": q.question_text,
            "order_num": q.order_num,
        }
        for q in questions
    ]


@router.post("/submit")
def submit_assessment(submit_data: Dict[str, Any], db: Session = Depends(get_db)):
    answers = submit_data.get("answers") or {}
    user_id: Optional[int] = submit_data.get("user_id")

    if user_id is not None:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在，无法保存能力评估结果")

    questions = db.query(AssessmentQuestion).all()
    question_map = {q.id: q for q in questions}

    dimension_scores: Dict[str, List[int]] = {dimension: [] for dimension in DIMENSION_NAMES}
    for question_id, score in answers.items():
        try:
            q_id = int(question_id)
            value = int(score)
        except (TypeError, ValueError):
            continue

        if q_id in question_map and 1 <= value <= 5:
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
    suggestions = (
        f"你的{DIMENSION_NAMES[strongest[0]]}较突出（{strongest[1]:.0f}分），"
        f"{DIMENSION_NAMES[weakest[0]]}还有提升空间（{weakest[1]:.0f}分）。"
        "建议结合目标职业要求，优先补强短板能力。"
    )

    record = AssessmentRecord(
        user_id=user_id,
        scores=raw_scores,
        answers=answers,
        overall_level=overall_level,
        suggestions=suggestions,
    )
    db.add(record)
    db.commit()

    return {
        "scores": raw_scores,
        "overall_level": overall_level,
        "suggestions": suggestions,
        "radar_data": raw_scores,
        "created_at": datetime.datetime.now().isoformat(),
    }


@router.get("/history/{user_id}")
def get_assessment_history(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )
    return [
        {
            "id": record.id,
            "scores": record.scores,
            "overall_level": record.overall_level,
            "created_at": record.created_at,
        }
        for record in records
    ]
