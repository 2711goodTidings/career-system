import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AssessmentRecord, Career, CareerPath, UserProfile
from schemas import (
    CareerCreate,
    CareerUpdate,
    CareerResponse,
    CareerRecommendationItem,
    CareerRecommendationResponse,
    AbilitySnapshot,
)

router = APIRouter()

# -----------------------------
# 路径关键词
# -----------------------------
PATH_KEYWORDS = {
    "就业": ["就业", "工作", "实习", "公司", "企业", "开发", "产品", "测试", "运营", "分析"],
    "考研": ["考研", "读研", "深造", "科研", "算法", "论文", "实验室", "学术"],
    "考公": ["考公", "公务员", "事业编", "编制", "体制", "政府", "行政", "稳定"],
    "留学": ["留学", "出国", "海外", "英语", "雅思", "托福", "国际", "国外"],
}

# -----------------------------
# 默认职业库
# -----------------------------
DEFAULT_CAREERS = [
    {
        "career_name": "后端开发工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件开发",
        "education_require": "本科及以上",
        "avg_salary": 12000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,人工智能,数据科学",
        "suitable_skills": "Python,Java,MySQL,FastAPI,Django,后端开发,数据库",
        "skill_require": "接口设计,数据库设计,后端框架,调试能力",
        "description": "负责系统接口、服务端逻辑和数据库设计开发。",
        "work_content": "后端开发、接口联调、数据库维护、性能优化",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "前端开发工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件开发",
        "education_require": "本科及以上",
        "avg_salary": 11000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,数字媒体技术",
        "suitable_skills": "Vue,JavaScript,HTML,CSS,前端开发,交互设计",
        "skill_require": "页面开发,组件设计,前后端联调,交互实现",
        "description": "负责 Web 页面开发与交互效果实现。",
        "work_content": "前端页面开发、组件封装、接口联调、页面优化",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "测试工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件测试",
        "education_require": "本科及以上",
        "avg_salary": 9000,
        "growth_potential": "中高",
        "suitable_major": "计算机,软件工程,信息管理",
        "suitable_skills": "测试,接口测试,功能测试,自动化测试,Python",
        "skill_require": "测试用例,缺陷跟踪,质量保障,自动化测试",
        "description": "负责系统测试、质量保障和缺陷管理。",
        "work_content": "编写测试用例、执行测试、提交缺陷、跟踪修复",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "数据分析师",
        "category": "就业岗位",
        "industry": "数据分析 / 商业分析",
        "education_require": "本科及以上",
        "avg_salary": 10000,
        "growth_potential": "高",
        "suitable_major": "计算机,统计学,数学,数据科学,信息管理",
        "suitable_skills": "SQL,Python,Excel,数据分析,可视化,统计",
        "skill_require": "数据处理,报表分析,可视化,业务理解",
        "description": "负责业务数据清洗、分析和可视化展示。",
        "work_content": "数据处理、统计分析、可视化报表、业务洞察",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "软件工程硕士方向",
        "category": "升学方向",
        "industry": "研究生深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程",
        "suitable_skills": "编程,项目开发,软件工程,系统设计",
        "skill_require": "专业基础,编程能力,逻辑能力,学习能力",
        "description": "适合希望继续深造并提升系统开发能力的学生。",
        "work_content": "研究生学习、课程研究、项目训练",
        "recommend_path": "考研",
        "is_active": True,
    },
    {
        "career_name": "人工智能硕士方向",
        "category": "升学方向",
        "industry": "研究生深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,人工智能,自动化,数据科学",
        "suitable_skills": "Python,算法,机器学习,深度学习,科研",
        "skill_require": "数学基础,算法能力,科研兴趣,英语阅读",
        "description": "适合对算法、模型和科研方向感兴趣的学生。",
        "work_content": "算法学习、科研训练、模型实验、论文阅读",
        "recommend_path": "考研",
        "is_active": True,
    },
    {
        "career_name": "计算机技术硕士方向",
        "category": "升学方向",
        "industry": "研究生深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,网络工程",
        "suitable_skills": "编程,系统开发,网络,数据库",
        "skill_require": "专业基础,实践能力,学习能力",
        "description": "偏应用型的计算机深造方向。",
        "work_content": "课程学习、项目实践、系统开发训练",
        "recommend_path": "考研",
        "is_active": True,
    },
    {
        "career_name": "数据科学硕士方向",
        "category": "升学方向",
        "industry": "研究生深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "数据科学,统计学,数学,计算机",
        "suitable_skills": "Python,SQL,统计,建模,数据分析",
        "skill_require": "统计基础,建模能力,数据处理能力",
        "description": "适合希望在数据分析、建模和智能分析方向继续深造的学生。",
        "work_content": "数据建模、统计分析、科研训练",
        "recommend_path": "考研",
        "is_active": True,
    },
    {
        "career_name": "信息化管理岗",
        "category": "体制岗位",
        "industry": "政府 / 事业单位",
        "education_require": "本科及以上",
        "avg_salary": 8000,
        "growth_potential": "中高",
        "suitable_major": "计算机,信息管理,电子信息",
        "suitable_skills": "办公软件,信息系统,沟通表达,执行力",
        "skill_require": "信息化管理,材料撰写,组织协调,执行能力",
        "description": "适合希望进入体制内从事信息化相关工作的学生。",
        "work_content": "信息系统维护、资料整理、行政协同、项目支持",
        "recommend_path": "考公",
        "is_active": True,
    },
    {
        "career_name": "综合管理岗",
        "category": "体制岗位",
        "industry": "政府 / 公共管理",
        "education_require": "本科及以上",
        "avg_salary": 7500,
        "growth_potential": "中",
        "suitable_major": "公共管理,法学,计算机,工商管理",
        "suitable_skills": "沟通,表达,写作,组织协调,执行力",
        "skill_require": "文书写作,组织协调,政策理解,稳定性",
        "description": "适合希望进入公共管理、行政服务类岗位的学生。",
        "work_content": "公文处理、事务协调、信息整理、综合管理",
        "recommend_path": "考公",
        "is_active": True,
    },
    {
        "career_name": "计算机科学留学方向",
        "category": "留学方向",
        "industry": "海外深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,人工智能",
        "suitable_skills": "英语,编程,算法,科研阅读",
        "skill_require": "英语能力,学术基础,项目经历,国际化适应",
        "description": "适合有出国深造意向的计算机相关专业学生。",
        "work_content": "海外申请、语言准备、项目背景提升、研究学习",
        "recommend_path": "留学",
        "is_active": True,
    },
    {
        "career_name": "数据科学留学方向",
        "category": "留学方向",
        "industry": "海外深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "数据科学,统计学,数学,计算机",
        "suitable_skills": "英语,Python,统计,建模,数据分析",
        "skill_require": "英语能力,建模能力,科研潜力,国际适应能力",
        "description": "适合希望赴海外继续深造数据分析与建模方向的学生。",
        "work_content": "留学申请、语言考试、科研准备、课程学习",
        "recommend_path": "留学",
        "is_active": True,
    },
]


# -----------------------------
# 工具函数
# -----------------------------
def split_keywords(text: str | None) -> List[str]:
    if not text:
        return []
    parts = re.split(r"[,，、/；;\s|]+", text.lower())
    result = []
    for item in parts:
        item = item.strip()
        if item and item not in result:
            result.append(item)
    return result


def text_has_keyword(text: str | None, keywords: List[str]) -> bool:
    source = (text or "").lower()
    return any(keyword.lower() in source for keyword in keywords)


def text_match_score(user_text: str | None, target_text: str | None, default_no_target: int = 60) -> float:
    user_set = set(split_keywords(user_text))
    target_set = set(split_keywords(target_text))

    if not target_set:
        return float(default_no_target)

    overlap = len(user_set & target_set)
    if overlap >= 3:
        return 100.0
    if overlap == 2:
        return 85.0
    if overlap == 1:
        return 70.0
    return 25.0


def get_default_ability_snapshot() -> dict:
    return {
        "logic": 75.0,
        "innovation": 70.0,
        "communication": 68.0,
        "learning": 72.0,
        "pressure": 66.0,
        "leadership": 64.0,
    }


def get_latest_ability_snapshot(user_id: int, db: Session) -> dict:
    ability = get_default_ability_snapshot()
    latest_record = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .first()
    )

    if latest_record and isinstance(latest_record.scores, dict):
        for key in ability:
            value = latest_record.scores.get(key)
            if isinstance(value, (int, float)):
                ability[key] = float(value)

    return ability


def calc_path_result(profile: UserProfile, db: Session):
    ability = get_latest_ability_snapshot(profile.user_id, db)

    ability_score_map = {
        "就业": round(
            0.30 * ability["communication"]
            + 0.25 * ability["learning"]
            + 0.25 * ability["logic"]
            + 0.20 * ability["pressure"],
            2,
        ),
        "考研": round(
            0.40 * ability["logic"]
            + 0.35 * ability["learning"]
            + 0.15 * ability["pressure"]
            + 0.10 * ability["innovation"],
            2,
        ),
        "考公": round(
            0.35 * ability["pressure"]
            + 0.25 * ability["communication"]
            + 0.25 * ability["leadership"]
            + 0.15 * ability["logic"],
            2,
        ),
        "留学": round(
            0.35 * ability["learning"]
            + 0.25 * ability["communication"]
            + 0.20 * ability["innovation"]
            + 0.20 * ability["pressure"],
            2,
        ),
    }

    text_blob = " ".join(
        [
            profile.interest or "",
            profile.skills or "",
            profile.career_goal or "",
            profile.bio or "",
        ]
    )

    def calc_preference_score(path_name: str) -> float:
        score = 35.0
        if (profile.target_preference or "").strip() == path_name:
            score += 45.0
        if text_has_keyword(text_blob, PATH_KEYWORDS[path_name]):
            score += 20.0
        return min(score, 100.0)

    def calc_match_score(path_name: str) -> float:
        return text_match_score(text_blob, ",".join(PATH_KEYWORDS[path_name]), default_no_target=40)

    score_map = {}
    for path_name in ["就业", "考研", "考公", "留学"]:
        score_map[path_name] = round(
            0.557 * ability_score_map[path_name]
            + 0.263 * calc_preference_score(path_name)
            + 0.180 * calc_match_score(path_name),
            2,
        )

    sorted_scores = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    top_path, top_score = sorted_scores[0]
    second_path, second_score = sorted_scores[1]

    path_reason_map = {
        "就业": "执行力与技能实践匹配更突出",
        "考研": "逻辑能力与研究倾向更占优势",
        "考公": "稳定性与沟通表达更适合体制型发展",
        "留学": "英语能力与国际化适应性更符合海外发展需求",
    }

    analysis_text = (
        f"根据你的专业背景、目标偏好与默认能力画像，当前更适合优先走{top_path}路径。"
        f"你的{path_reason_map[top_path]}；同时，{second_path}路径也具有一定潜力"
        f"（{top_score} vs {second_score}）。"
    )

    return ability, score_map, top_path, analysis_text


def score_career_for_user(profile: UserProfile, career: Career, recommend_path: str) -> CareerRecommendationItem:
    user_interest_text = " ".join([profile.interest or "", profile.career_goal or ""])
    user_skill_text = " ".join([profile.skills or "", profile.bio or ""])
    user_major_text = profile.major or ""

    major_match = text_match_score(user_major_text, career.suitable_major, default_no_target=50)

    career_skill_target = " ".join([career.suitable_skills or "", career.skill_require or ""])
    skill_match = text_match_score(user_skill_text, career_skill_target, default_no_target=55)

    interest_target = " ".join(
        [career.category or "", career.industry or "", career.description or "", career.work_content or ""]
    )
    interest_match = text_match_score(user_interest_text, interest_target, default_no_target=50)

    path_match = 100.0 if career.recommend_path == recommend_path else 40.0

    edu_match = 85.0
    edu_text = (career.education_require or "").lower()
    if not edu_text:
        edu_match = 80.0
    elif "本科" in edu_text:
        edu_match = 100.0
    elif "硕士" in edu_text or "研究生" in edu_text:
        edu_match = 65.0
    else:
        edu_match = 80.0

    match_score = round(
        0.35 * major_match
        + 0.25 * skill_match
        + 0.20 * interest_match
        + 0.10 * path_match
        + 0.10 * edu_match,
        2,
    )

    reasons = []
    if major_match >= 70:
        reasons.append("专业匹配度较高")
    if skill_match >= 70:
        reasons.append("技能关键词匹配较好")
    if interest_match >= 70:
        reasons.append("兴趣和发展目标较一致")
    if path_match >= 100:
        reasons.append("与当前推荐路径一致")
    if not reasons:
        reasons.append("与当前推荐结果具有基础匹配")

    user_skill_set = set(split_keywords(profile.skills))
    career_skill_set = set(split_keywords(career_skill_target))
    gap_skills = [item for item in career_skill_set if item not in user_skill_set][:3]

    return CareerRecommendationItem(
        career_id=career.career_id,
        career_name=career.career_name,
        category=career.category,
        industry=career.industry,
        education_require=career.education_require,
        avg_salary=career.avg_salary,
        growth_potential=career.growth_potential,
        suitable_major=career.suitable_major,
        suitable_skills=career.suitable_skills,
        skill_require=career.skill_require,
        description=career.description,
        work_content=career.work_content,
        recommend_path=career.recommend_path,
        is_active=career.is_active,
        match_score=match_score,
        reasons=reasons,
        gap_skills=gap_skills,
    )


def build_advice_list(recommend_path: str, career_items: List[CareerRecommendationItem]) -> List[str]:
    advice = []

    if recommend_path == "就业":
        advice.extend(
            [
                "建议优先补齐项目经验与简历内容，尽快形成可展示作品。",
                "可以围绕目标岗位补充 1~2 项核心技能并完成一次实习/项目训练。",
            ]
        )
    elif recommend_path == "考研":
        advice.extend(
            [
                "建议尽快明确报考方向，优先补专业课、数学或英语基础。",
                "可同步准备科研经历或课程项目，提升复试竞争力。",
            ]
        )
    elif recommend_path == "考公":
        advice.extend(
            [
                "建议提前了解目标岗位要求，重点准备行测、申论与材料表达能力。",
                "可同步关注信息化岗、综合管理岗等更适合自身背景的方向。",
            ]
        )
    elif recommend_path == "留学":
        advice.extend(
            [
                "建议尽快准备英语成绩与申请材料，提升语言与项目背景。",
                "可优先梳理个人陈述、简历与课程/科研经历。",
            ]
        )

    gap_pool = []
    for item in career_items:
        gap_pool.extend(item.gap_skills)

    unique_gaps = []
    for gap in gap_pool:
        if gap not in unique_gaps:
            unique_gaps.append(gap)

    if unique_gaps:
        advice.append("建议优先补强这些技能：" + "、".join(unique_gaps[:4]))

    return advice


def upsert_career_path(
    user_id: int,
    score_map: dict,
    recommend_path: str,
    analysis_text: str,
    db: Session,
) -> CareerPath:
    path_record = db.query(CareerPath).filter(CareerPath.user_id == user_id).first()

    if path_record:
        path_record.job_score = score_map["就业"]
        path_record.graduate_score = score_map["考研"]
        path_record.civil_service_score = score_map["考公"]
        path_record.abroad_score = score_map["留学"]
        path_record.recommend_path = recommend_path
        path_record.analysis_text = analysis_text
    else:
        path_record = CareerPath(
            user_id=user_id,
            job_score=score_map["就业"],
            graduate_score=score_map["考研"],
            civil_service_score=score_map["考公"],
            abroad_score=score_map["留学"],
            recommend_path=recommend_path,
            analysis_text=analysis_text,
        )
        db.add(path_record)

    db.commit()
    db.refresh(path_record)
    return path_record


# -----------------------------
# 原有 CRUD
# -----------------------------
@router.get("/", response_model=List[CareerResponse])
def get_all_careers(db: Session = Depends(get_db)):
    return db.query(Career).filter(Career.is_active == True).all()


@router.get("/seed-defaults")
def seed_default_careers(db: Session = Depends(get_db)):
    inserted = 0
    for item in DEFAULT_CAREERS:
        existing = db.query(Career).filter(Career.career_name == item["career_name"]).first()
        if existing:
            continue
        db.add(Career(**item))
        inserted += 1

    db.commit()
    return {"message": f"默认职业库初始化完成，本次新增 {inserted} 条数据"}


@router.get("/recommendation/{user_id}", response_model=CareerRecommendationResponse)
def get_career_recommendation(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先完善个人信息后再生成职业发展推荐")

    ability_snapshot_dict, score_map, recommend_path, analysis_text = calc_path_result(profile, db)

    path_record = upsert_career_path(
        user_id=user_id,
        score_map=score_map,
        recommend_path=recommend_path,
        analysis_text=analysis_text,
        db=db,
    )

    path_careers = (
        db.query(Career)
        .filter(Career.is_active == True, Career.recommend_path == recommend_path)
        .all()
    )

    candidate_careers = path_careers
    if not candidate_careers:
        candidate_careers = db.query(Career).filter(Career.is_active == True).all()

    scored_items = [score_career_for_user(profile, career, recommend_path) for career in candidate_careers]
    scored_items.sort(key=lambda x: x.match_score, reverse=True)
    career_list = scored_items[:3]

    advice_list = build_advice_list(recommend_path, career_list)

    ability_snapshot = AbilitySnapshot(**ability_snapshot_dict)

    return CareerRecommendationResponse(
        user_id=user_id,
        ability_snapshot=ability_snapshot,
        path_result=path_record,
        career_list=career_list,
        advice_list=advice_list,
    )


@router.get("/recommend/{user_id}", response_model=List[CareerResponse])
def recommend_careers(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先完善个人信息")

    _, score_map, recommend_path, analysis_text = calc_path_result(profile, db)

    upsert_career_path(
        user_id=user_id,
        score_map=score_map,
        recommend_path=recommend_path,
        analysis_text=analysis_text,
        db=db,
    )

    careers = (
        db.query(Career)
        .filter(Career.recommend_path == recommend_path, Career.is_active == True)
        .limit(3)
        .all()
    )

    if careers:
        return careers

    return db.query(Career).filter(Career.is_active == True).limit(3).all()


@router.get("/{career_id}", response_model=CareerResponse)
def get_career_detail(career_id: int, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.career_id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="职业不存在")
    return career


@router.post("/", response_model=CareerResponse)
def create_career(career_data: CareerCreate, db: Session = Depends(get_db)):
    new_career = Career(**career_data.model_dump())
    db.add(new_career)
    db.commit()
    db.refresh(new_career)
    return new_career


@router.put("/{career_id}", response_model=CareerResponse)
def update_career(career_id: int, career_data: CareerUpdate, db: Session = Depends(get_db)):
    career = db.query(Career).filter(Career.career_id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="职业不存在")

    update_data = career_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(career, key, value)

    db.commit()
    db.refresh(career)
    return career
