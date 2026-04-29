import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List, Any
from database import get_db
from models import User, UserProfile, AssessmentQuestion, AssessmentRecord
import json

router = APIRouter(prefix="/api/assessment", tags=["assessment"])

# 维度名称映射
DIMENSION_NAMES = {
    "logic": "逻辑思维",
    "innovation": "创新能力",
    "communication": "沟通协作",
    "learning": "学习能力",
    "pressure": "抗压能力",
    "leadership": "领导力"
}

# 预设题目
DEFAULT_QUESTIONS = [
    {"dimension": "logic", "question_text": "我能够快速理解复杂的概念和问题", "order_num": 1},
    {"dimension": "logic", "question_text": "我喜欢分析和解决需要推理的问题", "order_num": 2},
    {"dimension": "logic", "question_text": "我能够从多个角度思考同一个问题", "order_num": 3},
    {"dimension": "innovation", "question_text": "我经常能想到别人想不到的点子", "order_num": 4},
    {"dimension": "innovation", "question_text": "我喜欢尝试新的方法和思路", "order_num": 5},
    {"dimension": "innovation", "question_text": "面对问题，我总能找到独特的解决方案", "order_num": 6},
    {"dimension": "communication", "question_text": "我能够清晰地表达自己的想法", "order_num": 7},
    {"dimension": "communication", "question_text": "我善于倾听他人的意见", "order_num": 8},
    {"dimension": "communication", "question_text": "我在团队中能够很好地与他人合作", "order_num": 9},
    {"dimension": "learning", "question_text": "我学习新知识的速度很快", "order_num": 10},
    {"dimension": "learning", "question_text": "我能够主动寻找学习资源", "order_num": 11},
    {"dimension": "learning", "question_text": "我善于总结和归纳学到的知识", "order_num": 12},
    {"dimension": "pressure", "question_text": "面对压力时我能保持冷静", "order_num": 13},
    {"dimension": "pressure", "question_text": "我能够很好地应对突发状况", "order_num": 14},
    {"dimension": "pressure", "question_text": "失败后我能够快速调整心态", "order_num": 15},
    {"dimension": "leadership", "question_text": "我能够影响和带动身边的人", "order_num": 16},
    {"dimension": "leadership", "question_text": "我愿意承担责任", "order_num": 17},
    {"dimension": "leadership", "question_text": "我能够协调团队资源达成目标", "order_num": 18},
]

@router.on_event("startup")
async def init_questions():
    """启动时初始化题目"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        existing = db.query(AssessmentQuestion).first()
        if not existing:
            for q in DEFAULT_QUESTIONS:
                question = AssessmentQuestion(**q)
                db.add(question)
            db.commit()
            print("✅ 已初始化评估题目（18道）")
    except Exception as e:
        print(f"初始化题目失败: {e}")
    finally:
        db.close()

@router.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    """获取所有评估题目 - 无需登录"""
    questions = db.query(AssessmentQuestion).order_by(AssessmentQuestion.order_num).all()
    return [
        {
            "id": q.id,
            "dimension": q.dimension,
            "question_text": q.question_text,
            "order_num": q.order_num
        }
        for q in questions
    ]

@router.post("/submit")
def submit_assessment(
    submit_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """提交能力评估 - 无需登录"""
    
    answers = submit_data.get("answers", {})
    
    # 获取所有题目
    questions = db.query(AssessmentQuestion).all()
    q_dict = {q.id: q for q in questions}
    
    # 按维度统计原始得分
    dimension_scores: Dict[str, List[int]] = {dim: [] for dim in DIMENSION_NAMES.keys()}
    for q_id_str, score in answers.items():
        q_id = int(q_id_str)
        if q_id in q_dict:
            dim = q_dict[q_id].dimension
            dimension_scores[dim].append(int(score))
    
    # 计算各维度百分制得分
    raw_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            raw_scores[dim] = (avg / 5) * 100
        else:
            raw_scores[dim] = 50
    
    # 确定综合等级
    avg_score = sum(raw_scores.values()) / len(raw_scores)
    if avg_score >= 85:
        overall_level = "优秀"
    elif avg_score >= 70:
        overall_level = "良好"
    elif avg_score >= 55:
        overall_level = "中等"
    else:
        overall_level = "待提升"
    
    # 生成建议
    strongest = max(raw_scores.items(), key=lambda x: x[1])
    weakest = min(raw_scores.items(), key=lambda x: x[1])
    
    suggestions = f"""根据您的评估结果，您的{DIMENSION_NAMES[strongest[0]]}能力最为突出（{strongest[1]:.0f}分）。
{DIMENSION_NAMES[weakest[0]]}能力还有提升空间（{weakest[1]:.0f}分），建议多加练习。
"""
    
    # 保存评估记录（使用临时用户ID或session）
    # 如果没有登录，可以使用临时ID或跳过保存
    try:
        record = AssessmentRecord(
            user_id=1,  # 临时用户ID，您可以修改为从session获取
            scores=raw_scores,
            answers=answers,
            overall_level=overall_level,
            suggestions=suggestions
        )
        db.add(record)
        db.commit()
    except Exception as e:
        print(f"保存记录失败: {e}")
        db.rollback()
    
    return {
        "scores": raw_scores,
        "overall_level": overall_level,
        "suggestions": suggestions,
        "radar_data": raw_scores,
        "created_at": datetime.datetime.now().isoformat()
    }