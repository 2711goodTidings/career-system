import re
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AssessmentRecord, Career, CareerPath, UserProfile
from schemas import (
    CareerCreate,
    CareerUpdate,
    CareerResponse,
    CareerPlanningInput,
    CareerRecommendationItem,
    CareerRecommendationResponse,
    RecommendationDataSource,
    AbilitySnapshot,
)

router = APIRouter()

# -----------------------------
# 路径关键词
# -----------------------------
PATH_KEYWORDS = {
    "就业": ["就业", "工作", "实习", "互联网", "软件", "开发", "前端", "后端", "测试", "数据", "安全", "运维", "算法", "产品"],
    "考研": ["考研", "读研", "深造", "计算机", "408", "数据结构", "操作系统", "计算机网络", "组成原理", "算法", "科研", "实验室"],
    "考公": ["考公", "公务员", "事业编", "编制", "体制", "政府", "信息化", "数字政务", "网络安全", "数据治理", "稳定"],
    "留学": ["留学", "出国", "海外", "英语", "雅思", "托福", "计算机科学", "cs", "软件工程", "数据科学", "科研", "项目背景"],
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
        "avg_salary": 14000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,网络工程,人工智能,数据科学",
        "suitable_skills": "Java,Python,Go,Spring Boot,FastAPI,MySQL,Redis,Linux,后端开发",
        "skill_require": "数据结构,接口设计,数据库设计,后端框架,缓存,调试能力",
        "description": "负责服务端业务逻辑、接口、数据库和系统性能优化。",
        "work_content": "接口开发、数据库建模、权限与日志、服务部署、性能排查",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "前端开发工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件开发",
        "education_require": "本科及以上",
        "avg_salary": 12000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,数字媒体技术",
        "suitable_skills": "Vue,React,JavaScript,TypeScript,HTML,CSS,前端工程化",
        "skill_require": "组件开发,状态管理,路由,接口联调,浏览器调试,工程化构建",
        "description": "负责 Web 页面、组件、交互和前端工程化实现。",
        "work_content": "页面开发、组件封装、接口联调、性能优化、移动端适配",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "全栈开发工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件开发",
        "education_require": "本科及以上",
        "avg_salary": 15000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,网络工程",
        "suitable_skills": "Vue,React,Java,Python,Node.js,MySQL,前后端联调,系统设计",
        "skill_require": "前端开发,后端开发,数据库设计,接口联调,部署运维",
        "description": "负责从页面到服务端的完整功能开发，适合项目实践较强的学生。",
        "work_content": "需求拆解、前端页面、后端接口、数据库、部署上线",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "测试开发工程师",
        "category": "就业岗位",
        "industry": "互联网 / 软件测试",
        "education_require": "本科及以上",
        "avg_salary": 11000,
        "growth_potential": "中高",
        "suitable_major": "计算机,软件工程,信息管理",
        "suitable_skills": "Python,Java,接口测试,自动化测试,性能测试,CI/CD",
        "skill_require": "测试用例,接口测试,自动化脚本,缺陷定位,质量保障",
        "description": "负责测试平台、自动化测试和质量保障，要求兼具编码与测试思维。",
        "work_content": "编写测试用例、开发测试脚本、接口测试、缺陷跟踪、质量分析",
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
        "suitable_skills": "SQL,Python,Excel,Pandas,可视化,统计分析,业务分析",
        "skill_require": "SQL查询,数据清洗,指标分析,可视化报表,业务理解",
        "description": "负责业务数据清洗、指标分析和可视化展示。",
        "work_content": "数据处理、统计分析、报表搭建、业务洞察、汇报表达",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "数据开发工程师",
        "category": "就业岗位",
        "industry": "大数据 / 数据平台",
        "education_require": "本科及以上",
        "avg_salary": 15000,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,数据科学,信息管理",
        "suitable_skills": "SQL,Python,Java,Linux,Hadoop,Spark,数据仓库,ETL",
        "skill_require": "数据库,数据建模,ETL,分布式计算,任务调度",
        "description": "负责数据采集、清洗、建模、仓库建设和数据服务开发。",
        "work_content": "数据管道开发、离线任务、数据仓库、指标口径维护",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "AI 应用工程师",
        "category": "就业岗位",
        "industry": "人工智能 / 应用开发",
        "education_require": "本科及以上",
        "avg_salary": 16000,
        "growth_potential": "高",
        "suitable_major": "计算机,人工智能,软件工程,数据科学",
        "suitable_skills": "Python,机器学习,深度学习,大模型,RAG,FastAPI,向量数据库",
        "skill_require": "Python编程,模型调用,提示词工程,数据处理,应用集成",
        "description": "负责把机器学习或大模型能力接入实际业务应用。",
        "work_content": "模型接口调用、知识库问答、数据处理、AI 功能后端开发",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "网络安全工程师",
        "category": "就业岗位",
        "industry": "网络安全",
        "education_require": "本科及以上",
        "avg_salary": 13000,
        "growth_potential": "高",
        "suitable_major": "计算机,网络工程,信息安全,软件工程",
        "suitable_skills": "Linux,计算机网络,Web安全,渗透测试,Python,安全加固",
        "skill_require": "网络基础,漏洞分析,日志分析,攻防演练,安全工具",
        "description": "负责系统安全防护、漏洞排查、攻防演练和安全运营。",
        "work_content": "安全测试、漏洞修复、日志监控、应急响应、安全方案落地",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "运维 / DevOps 工程师",
        "category": "就业岗位",
        "industry": "云计算 / 运维平台",
        "education_require": "本科及以上",
        "avg_salary": 13000,
        "growth_potential": "中高",
        "suitable_major": "计算机,软件工程,网络工程",
        "suitable_skills": "Linux,Docker,Kubernetes,Shell,CI/CD,云服务,监控",
        "skill_require": "Linux运维,容器化,自动化部署,监控告警,故障排查",
        "description": "负责应用部署、自动化运维、监控和系统稳定性保障。",
        "work_content": "服务部署、流水线配置、监控告警、故障处理、资源优化",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "嵌入式开发工程师",
        "category": "就业岗位",
        "industry": "智能硬件 / 物联网",
        "education_require": "本科及以上",
        "avg_salary": 13000,
        "growth_potential": "中高",
        "suitable_major": "计算机,电子信息,自动化,物联网工程",
        "suitable_skills": "C,C++,单片机,Linux,操作系统,计算机组成,硬件调试",
        "skill_require": "C语言,嵌入式Linux,驱动基础,硬件接口,调试能力",
        "description": "负责智能硬件、物联网设备或底层系统的软件开发。",
        "work_content": "驱动开发、协议适配、设备调试、嵌入式应用开发",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "产品经理",
        "category": "就业岗位",
        "industry": "互联网 / 软件产品",
        "education_require": "本科及以上",
        "avg_salary": 12000,
        "growth_potential": "中高",
        "suitable_major": "计算机,软件工程,信息管理,工商管理",
        "suitable_skills": "需求分析,原型设计,用户研究,数据分析,沟通表达,技术理解",
        "skill_require": "需求文档,原型工具,业务分析,项目协作,技术沟通",
        "description": "负责软件产品需求分析、方案设计和研发协作。",
        "work_content": "需求调研、原型设计、PRD 编写、项目推进、数据复盘",
        "recommend_path": "就业",
        "is_active": True,
    },
    {
        "career_name": "考研深造方向",
        "category": "升学方向",
        "industry": "计算机研究生深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,人工智能,网络工程,数据科学",
        "suitable_skills": "数据结构,操作系统,计算机网络,计算机组成原理,数学,英语,编程",
        "skill_require": "408专业课,数学,英语,算法基础,复试项目表达",
        "description": "适合希望通过考研提升学历、专业基础和研究能力的学生。",
        "work_content": "专业课复习、数学英语备考、目标院校选择、复试项目准备",
        "recommend_path": "考研",
        "is_active": True,
    },
    {
        "career_name": "考公信息化岗位",
        "category": "体制岗位",
        "industry": "政府 / 事业单位信息化",
        "education_require": "本科及以上",
        "avg_salary": 8000,
        "growth_potential": "中高",
        "suitable_major": "计算机,软件工程,网络工程,信息安全,信息管理",
        "suitable_skills": "计算机基础,信息系统,网络安全,数据库,公文写作,行测,申论",
        "skill_require": "行测,申论,信息化管理,网络安全基础,材料表达",
        "description": "适合希望进入体制内从事数字政务、信息系统或网络安全相关工作的学生。",
        "work_content": "信息系统维护、数字政务项目支持、网络安全管理、材料撰写",
        "recommend_path": "考公",
        "is_active": True,
    },
    {
        "career_name": "留学计算机方向",
        "category": "留学方向",
        "industry": "海外计算机深造",
        "education_require": "本科",
        "avg_salary": None,
        "growth_potential": "高",
        "suitable_major": "计算机,软件工程,人工智能,数据科学,网络安全",
        "suitable_skills": "英语,托福,雅思,编程,算法,科研阅读,项目经历,GPA",
        "skill_require": "语言成绩,GPA,项目背景,推荐信,个人陈述,英语技术阅读",
        "description": "适合有海外计算机、软件工程、数据科学或 AI 深造意向的学生。",
        "work_content": "语言考试、选校定位、项目背景提升、文书准备、课程衔接",
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


def weighted_ability_score(ability: dict, weights: dict) -> float:
    total_weight = sum(weights.values()) or 1
    return round(sum(float(ability.get(key, 60.0)) * weight for key, weight in weights.items()) / total_weight, 2)


def clamp_score(value: float) -> float:
    return round(min(100.0, max(0.0, value)), 2)


def score_academic(planning_input: CareerPlanningInput | None) -> float:
    data = planning_input_to_dict(planning_input)
    if not data:
        return 60.0

    gpa = float(data.get("gpa_score") or 0)
    rank = data.get("rank_level", "")
    if gpa >= 3.7 or rank == "前10%":
        return 95.0
    if gpa >= 3.3 or rank == "前30%":
        return 82.0
    if gpa >= 2.8 or rank == "前50%":
        return 68.0
    if gpa > 0 or rank == "50%以后":
        return 50.0
    return 60.0


def score_english(planning_input: CareerPlanningInput | None) -> float:
    data = planning_input_to_dict(planning_input)
    if not data:
        return 55.0

    cet4 = int(data.get("cet4_score") or 0)
    cet6 = int(data.get("cet6_score") or 0)
    language_test = data.get("language_test", "")

    score = 35.0
    if cet4 >= 425:
        score = max(score, 60.0)
    if cet4 >= 500:
        score = max(score, 70.0)
    if cet6 >= 425:
        score = max(score, 78.0)
    if cet6 >= 520:
        score = max(score, 88.0)
    if "雅思" in language_test or "托福" in language_test:
        score = max(score, 90.0)
    return score


def score_project_experience(planning_input: CareerPlanningInput | None) -> float:
    data = planning_input_to_dict(planning_input)
    if not data:
        return 55.0

    count = int(data.get("project_count") or 0)
    complexity = data.get("project_complexity", "")
    deployed = data.get("has_deployment", "")
    internship = data.get("internship_status", "")

    score = 35.0 + min(count, 3) * 12
    complexity_bonus = {
        "课程小作业": 5,
        "完整 CRUD 项目": 15,
        "前后端联调项目": 22,
        "上线/部署项目": 28,
        "科研/竞赛项目": 25,
    }
    score += complexity_bonus.get(complexity, 0)
    if deployed == "是":
        score += 10
    if internship == "校内/实验室经历":
        score += 8
    elif internship == "一段实习":
        score += 14
    elif internship == "多段实习":
        score += 20
    return clamp_score(score)


def score_constraint_fit(path_name: str, planning_input: CareerPlanningInput | None) -> float:
    data = planning_input_to_dict(planning_input)
    if not data:
        return 60.0

    economic = data.get("economic_constraint", "")
    value = data.get("value_preference", "")

    score = 55.0
    if path_name == "就业":
        if "需要尽快就业" in economic:
            score += 28
        if "高薪" in value or "城市机会" in value:
            score += 14
        if "低压力" in value:
            score -= 8
    elif path_name == "考研":
        if "可接受考研" in economic or "研究" in value:
            score += 28
        if "需要尽快就业" in economic:
            score -= 15
    elif path_name == "考公":
        if "稳定" in economic or "稳定" in value or "低压力" in value:
            score += 30
        if "高薪" in value:
            score -= 8
    elif path_name == "留学":
        if "可承担留学成本" in economic:
            score += 32
        if "需要尽快就业" in economic:
            score -= 20
    return clamp_score(score)


def score_path_interest(path_name: str, profile: UserProfile, planning_input: CareerPlanningInput | None) -> float:
    explicit_path = normalize_path_preference(profile.target_preference)
    text = " ".join(
        [
            profile.interest or "",
            profile.skills or "",
            profile.career_goal or "",
            profile.bio or "",
            (planning_input.tech_interests if planning_input else "") or "",
            (planning_input.extra_notes if planning_input else "") or "",
        ]
    )

    score = 45.0
    if explicit_path == path_name:
        score += 45.0
    elif explicit_path:
        score -= 12.0
    if text_has_keyword(text, PATH_KEYWORDS[path_name]):
        score += 18.0
    return clamp_score(score)


def calc_path_components(
    path_name: str,
    ability_score: float,
    profile: UserProfile,
    planning_input: CareerPlanningInput | None,
) -> dict:
    academic = score_academic(planning_input)
    english = score_english(planning_input)
    project = score_project_experience(planning_input)
    interest = score_path_interest(path_name, profile, planning_input)
    constraint = score_constraint_fit(path_name, planning_input)

    if path_name == "就业":
        weights = {
            "ability": 0.28,
            "interest": 0.24,
            "project": 0.26,
            "academic": 0.08,
            "english": 0.04,
            "constraint": 0.10,
        }
    elif path_name == "考研":
        weights = {
            "ability": 0.30,
            "interest": 0.26,
            "project": 0.08,
            "academic": 0.22,
            "english": 0.08,
            "constraint": 0.06,
        }
    elif path_name == "考公":
        weights = {
            "ability": 0.24,
            "interest": 0.24,
            "project": 0.08,
            "academic": 0.10,
            "english": 0.04,
            "constraint": 0.30,
        }
    else:
        weights = {
            "ability": 0.24,
            "interest": 0.20,
            "project": 0.16,
            "academic": 0.16,
            "english": 0.18,
            "constraint": 0.06,
        }

    components = {
        "ability": ability_score,
        "interest": interest,
        "project": project,
        "academic": academic,
        "english": english,
        "constraint": constraint,
    }
    total = sum(components[key] * weight for key, weight in weights.items())
    components["total"] = clamp_score(total)
    return components


def tech_weighted_score(ability: dict, weights: dict, fallback_weights: dict | None = None) -> float:
    tech_scores = ability.get("tech_scores") if isinstance(ability.get("tech_scores"), dict) else {}
    available = {key: weight for key, weight in weights.items() if isinstance(tech_scores.get(key), (int, float))}
    if available:
        total_weight = sum(available.values()) or 1
        return round(sum(float(tech_scores[key]) * weight for key, weight in available.items()) / total_weight, 2)
    return weighted_ability_score(ability, fallback_weights or {"logic": 0.34, "innovation": 0.22, "learning": 0.22, "pressure": 0.12, "communication": 0.10})


def has_general_assessment(ability: dict) -> bool:
    general_scores = ability.get("general_scores")
    return isinstance(general_scores, dict) and bool(general_scores)


def general_weighted_score(ability: dict, weights: dict) -> float:
    general_scores = ability.get("general_scores") if isinstance(ability.get("general_scores"), dict) else {}
    available = {key: weight for key, weight in weights.items() if isinstance(general_scores.get(key), (int, float))}
    if available:
        total_weight = sum(available.values()) or 1
        return round(sum(float(general_scores[key]) * weight for key, weight in available.items()) / total_weight, 2)
    return weighted_ability_score(ability, weights)


def calc_career_ability_match(career: Career, ability: dict) -> float:
    text = " ".join(
        [
            career.career_name or "",
            career.category or "",
            career.industry or "",
            career.suitable_skills or "",
            career.skill_require or "",
            career.description or "",
        ]
    )

    if any(keyword in text for keyword in ["后端", "全栈"]):
        return tech_weighted_score(
            ability,
            {"programming": 0.22, "backend": 0.24, "database": 0.18, "software_eng": 0.14, "computer_basic": 0.12, "devops": 0.10},
            {"logic": 0.28, "innovation": 0.24, "learning": 0.18, "pressure": 0.18, "communication": 0.12},
        )
    if "数据开发" in text:
        return tech_weighted_score(
            ability,
            {"programming": 0.18, "database": 0.30, "backend": 0.14, "computer_basic": 0.14, "software_eng": 0.12, "devops": 0.12},
            {"logic": 0.28, "innovation": 0.24, "learning": 0.18, "pressure": 0.18, "communication": 0.12},
        )
    elif "前端" in text:
        return tech_weighted_score(
            ability,
            {"frontend": 0.34, "programming": 0.18, "software_eng": 0.16, "backend": 0.10, "database": 0.08, "network": 0.08, "devops": 0.06},
            {"innovation": 0.28, "communication": 0.20, "learning": 0.18, "logic": 0.18, "pressure": 0.16},
        )
    elif any(keyword in text for keyword in ["AI", "人工智能"]):
        return tech_weighted_score(
            ability,
            {"ai_ml": 0.34, "algorithm": 0.24, "programming": 0.16, "computer_basic": 0.12, "database": 0.08, "software_eng": 0.06},
            {"logic": 0.30, "learning": 0.28, "innovation": 0.18, "communication": 0.12, "pressure": 0.12},
        )
    elif "数据分析" in text:
        return tech_weighted_score(
            ability,
            {"database": 0.28, "programming": 0.20, "ai_ml": 0.18, "algorithm": 0.12, "software_eng": 0.10, "computer_basic": 0.12},
            {"logic": 0.30, "learning": 0.28, "innovation": 0.18, "communication": 0.12, "pressure": 0.12},
        )
    elif "安全" in text:
        return tech_weighted_score(
            ability,
            {"network": 0.30, "computer_basic": 0.20, "programming": 0.16, "devops": 0.14, "backend": 0.10, "software_eng": 0.10},
            {"pressure": 0.26, "learning": 0.22, "logic": 0.20, "innovation": 0.20, "communication": 0.12},
        )
    elif any(keyword in text for keyword in ["运维", "DevOps"]):
        return tech_weighted_score(
            ability,
            {"devops": 0.34, "network": 0.22, "computer_basic": 0.16, "backend": 0.10, "database": 0.10, "software_eng": 0.08},
            {"pressure": 0.26, "learning": 0.22, "logic": 0.20, "innovation": 0.20, "communication": 0.12},
        )
    elif "嵌入式" in text:
        return tech_weighted_score(
            ability,
            {"programming": 0.28, "computer_basic": 0.28, "network": 0.12, "algorithm": 0.12, "software_eng": 0.10, "devops": 0.10},
            {"pressure": 0.26, "learning": 0.22, "logic": 0.20, "innovation": 0.20, "communication": 0.12},
        )
    elif any(keyword in text for keyword in ["产品", "考公", "信息化"]):
        weights = {"communication": 0.28, "leadership": 0.24, "learning": 0.18, "pressure": 0.18, "logic": 0.12}
    else:
        weights = {"logic": 0.20, "innovation": 0.20, "communication": 0.15, "learning": 0.20, "pressure": 0.15, "leadership": 0.10}

    return weighted_ability_score(ability, weights)


def calc_career_general_match(career: Career, ability: dict) -> float:
    text = " ".join(
        [
            career.career_name or "",
            career.category or "",
            career.industry or "",
            career.description or "",
            career.work_content or "",
        ]
    )

    if any(keyword in text for keyword in ["产品", "考公", "信息化", "售前", "技术支持"]):
        weights = {"communication": 0.30, "leadership": 0.24, "pressure": 0.20, "learning": 0.16, "logic": 0.10}
    elif any(keyword in text for keyword in ["前端", "全栈", "测试", "数据分析"]):
        weights = {"communication": 0.24, "learning": 0.22, "logic": 0.20, "pressure": 0.18, "innovation": 0.16}
    elif any(keyword in text for keyword in ["AI", "人工智能", "算法", "考研", "留学"]):
        weights = {"learning": 0.30, "logic": 0.26, "pressure": 0.18, "innovation": 0.16, "communication": 0.10}
    else:
        weights = {"learning": 0.24, "logic": 0.22, "pressure": 0.20, "communication": 0.18, "innovation": 0.16}

    return general_weighted_score(ability, weights)


def blend_career_ability_match(career: Career, tech_score: float, general_score: float, ability: dict) -> float:
    if not has_general_assessment(ability):
        return tech_score

    text = " ".join(
        [
            career.career_name or "",
            career.category or "",
            career.industry or "",
            career.description or "",
        ]
    )
    if any(keyword in text for keyword in ["产品", "考公", "信息化", "售前", "技术支持"]):
        general_weight = 0.42
    elif any(keyword in text for keyword in ["前端", "全栈", "测试", "数据分析"]):
        general_weight = 0.28
    else:
        general_weight = 0.22

    return clamp_score(tech_score * (1 - general_weight) + general_score * general_weight)


def calc_planning_input_career_match(career: Career, planning_input: CareerPlanningInput | None) -> float:
    data = planning_input_to_dict(planning_input)
    if not data:
        return 60.0

    career_text = " ".join(
        [
            career.career_name or "",
            career.category or "",
            career.industry or "",
            career.suitable_skills or "",
            career.skill_require or "",
            career.description or "",
        ]
    )
    user_text = " ".join(str(value) for value in data.values())
    score = text_match_score(user_text, career_text, default_no_target=45)

    project_count = int(data.get("project_count") or 0)
    project_complexity = data.get("project_complexity", "")
    internship = data.get("internship_status", "")
    deployment = data.get("has_deployment", "")
    cet4 = int(data.get("cet4_score") or 0)
    cet6 = int(data.get("cet6_score") or 0)
    language_test = data.get("language_test", "")
    economic = data.get("economic_constraint", "")
    value = data.get("value_preference", "")
    tech_interests = data.get("tech_interests", "")
    extra_notes = data.get("extra_notes", "")
    target_text = f"{tech_interests} {extra_notes}"

    direction_keywords = {
        "后端": ["后端", "Java", "Spring", "Python", "FastAPI", "接口", "服务器"],
        "前端": ["前端", "Vue", "React", "页面", "交互", "小程序"],
        "全栈": ["全栈", "前后端", "前端", "后端"],
        "测试": ["测试", "自动化测试", "质量", "测试开发"],
        "数据分析": ["数据分析", "可视化", "SQL", "指标", "商业分析"],
        "数据开发": ["数据开发", "大数据", "数仓", "ETL", "Spark"],
        "AI": ["AI", "人工智能", "大模型", "机器学习", "深度学习", "算法"],
        "网络安全": ["安全", "网络安全", "渗透", "攻防", "Web安全"],
        "运维": ["运维", "DevOps", "Linux", "Docker", "Kubernetes", "云"],
        "嵌入式": ["嵌入式", "单片机", "C语言", "硬件", "物联网"],
        "产品": ["产品", "需求", "原型", "用户", "PRD"],
    }

    for direction, keywords in direction_keywords.items():
        career_hit = direction in career_text or any(keyword in career_text for keyword in keywords)
        user_hit = any(keyword.lower() in target_text.lower() for keyword in keywords)
        if career_hit and user_hit:
            score += 22
        elif career_hit and target_text.strip() and not user_hit:
            score -= 10

    if career.recommend_path == "就业":
        if project_count >= 2:
            score += 10
        if "实习" in internship:
            score += 8
        if "部署" in project_complexity or deployment == "是":
            score += 6
        if "需要尽快就业" in economic or "高薪" in value:
            score += 6
    elif career.recommend_path == "考研":
        if "研究" in value or "可接受考研" in economic:
            score += 10
        if float(data.get("gpa_score") or 0) >= 3.2 or data.get("rank_level") in ["前10%", "前30%"]:
            score += 4
    elif career.recommend_path == "考公":
        if "稳定" in value or "稳定" in economic:
            score += 12
    elif career.recommend_path == "留学":
        if "可承担留学成本" in economic:
            score += 10
        if cet6 >= 425 or "雅思" in language_test or "托福" in language_test:
            score += 8

    return round(min(100.0, max(0.0, score)), 2)


def apply_planning_input_to_scores(score_map: dict, planning_input: CareerPlanningInput | None) -> dict:
    adjusted = dict(score_map)
    data = planning_input_to_dict(planning_input)
    if not data:
        return adjusted

    economic = data.get("economic_constraint", "")
    value = data.get("value_preference", "")
    cet4 = int(data.get("cet4_score") or 0)
    cet6 = int(data.get("cet6_score") or 0)
    language_test = data.get("language_test", "")
    project_count = int(data.get("project_count") or 0)
    internship = data.get("internship_status", "")
    project_complexity = data.get("project_complexity", "")
    deployment = data.get("has_deployment", "")
    tech_interests = data.get("tech_interests", "")
    extra_notes = data.get("extra_notes", "")
    text = " ".join(str(item) for item in [economic, value, language_test, project_complexity, internship, tech_interests, extra_notes])

    if "需要尽快就业" in economic or "高薪" in value or project_count >= 2 or "实习" in internship:
        adjusted["就业"] += 12
    if "部署" in project_complexity or deployment == "是":
        adjusted["就业"] += 8
    if "可接受考研" in economic or "研究" in value or "考研" in text:
        adjusted["考研"] += 14
    if cet6 >= 425 or "雅思" in language_test or "托福" in language_test or "可承担留学成本" in economic:
        adjusted["留学"] += 12
    if cet4 >= 425 or cet6 >= 425:
        adjusted["考研"] += 5
    if "稳定" in economic or "稳定" in value or "考公" in text or "体制" in text:
        adjusted["考公"] += 14
    if "AI" in tech_interests or "人工智能" in tech_interests or "算法" in tech_interests:
        adjusted["考研"] += 8
    if "后端" in tech_interests or "前端" in tech_interests or "测试" in tech_interests or "运维" in tech_interests:
        adjusted["就业"] += 8
    if project_count == 0 and "需要尽快就业" not in economic:
        adjusted["就业"] -= 4

    return {key: round(min(100.0, max(0.0, value)), 2) for key, value in adjusted.items()}


def normalize_path_preference(value: str | None) -> str:
    text = (value or "").strip()
    if text == "出国":
        return "留学"
    return text


def get_default_ability_snapshot() -> dict:
    return {
        "logic": 60.0,
        "innovation": 60.0,
        "communication": 60.0,
        "learning": 60.0,
        "pressure": 60.0,
        "leadership": 60.0,
        "tech_scores": {},
        "general_scores": {},
    }


def clean_score_map(scores: dict | None) -> dict:
    if not isinstance(scores, dict):
        return {}
    return {
        key: float(value)
        for key, value in scores.items()
        if isinstance(value, (int, float))
    }


def infer_assessment_type(scores: dict | None) -> str:
    score_map = scores if isinstance(scores, dict) else {}
    explicit_type = score_map.get("assessment_type")
    if explicit_type in ["general", "tech"]:
        return explicit_type
    if any(key in score_map for key in ["programming", "algorithm", "computer_basic", "backend", "frontend"]):
        return "tech"
    if any(key in score_map for key in ["logic", "innovation", "communication", "learning", "pressure", "leadership"]):
        return "tech"
    return "general"


def get_latest_assessment_record_by_type(user_id: int, assessment_type: str, db: Session) -> AssessmentRecord | None:
    records = (
        db.query(AssessmentRecord)
        .filter(AssessmentRecord.user_id == user_id)
        .order_by(AssessmentRecord.created_at.desc())
        .all()
    )
    for record in records:
        if infer_assessment_type(record.scores) == assessment_type:
            return record
    return None


def build_ability_from_assessments(
    tech_record: AssessmentRecord | None,
    general_record: AssessmentRecord | None,
) -> dict:
    ability = get_default_ability_snapshot()
    tech_scores = clean_score_map(tech_record.scores if tech_record else None)
    general_scores = clean_score_map(general_record.scores if general_record else None)

    if tech_scores:
        if any(key in tech_scores for key in ["programming", "algorithm", "computer_basic"]):
            ability["logic"] = round(0.45 * tech_scores.get("programming", 60.0) + 0.55 * tech_scores.get("algorithm", 60.0), 2)
            ability["innovation"] = round(
                0.28 * tech_scores.get("software_eng", 60.0)
                + 0.24 * tech_scores.get("backend", 60.0)
                + 0.20 * tech_scores.get("frontend", 60.0)
                + 0.18 * tech_scores.get("database", 60.0)
                + 0.10 * tech_scores.get("devops", 60.0),
                2,
            )
            ability["learning"] = round(
                0.45 * tech_scores.get("computer_basic", 60.0)
                + 0.20 * tech_scores.get("network", 60.0)
                + 0.20 * tech_scores.get("database", 60.0)
                + 0.15 * tech_scores.get("ai_ml", 60.0),
                2,
            )
            ability["pressure"] = round(
                0.38 * tech_scores.get("devops", 60.0)
                + 0.24 * tech_scores.get("network", 60.0)
                + 0.20 * tech_scores.get("software_eng", 60.0)
                + 0.18 * tech_scores.get("computer_basic", 60.0),
                2,
            )
        else:
            for key in ["logic", "innovation", "communication", "learning", "pressure", "leadership"]:
                if key in tech_scores:
                    ability[key] = round(tech_scores[key], 2)

    if general_scores:
        ability["communication"] = round(general_scores.get("communication", 60.0), 2)
        ability["leadership"] = round(
            0.50 * general_scores.get("leadership", 60.0)
            + 0.25 * general_scores.get("learning", 60.0)
            + 0.25 * general_scores.get("pressure", 60.0),
            2,
        )
        ability["logic"] = round(0.82 * ability["logic"] + 0.18 * general_scores.get("logic", 60.0), 2)
        ability["pressure"] = round(0.75 * ability["pressure"] + 0.25 * general_scores.get("pressure", 60.0), 2)
    elif tech_scores:
        ability["communication"] = round(
            0.45 * tech_scores.get("software_eng", 60.0)
            + 0.30 * tech_scores.get("frontend", 60.0)
            + 0.25 * tech_scores.get("backend", 60.0),
            2,
        )
        ability["leadership"] = round(
            0.45 * tech_scores.get("software_eng", 60.0)
            + 0.30 * tech_scores.get("devops", 60.0)
            + 0.25 * tech_scores.get("computer_basic", 60.0),
            2,
        )

    ability["tech_scores"] = tech_scores
    ability["general_scores"] = general_scores
    return ability


def get_latest_assessment_record(user_id: int, db: Session) -> AssessmentRecord | None:
    return get_latest_assessment_record_by_type(user_id, "tech", db)


def planning_input_to_dict(planning_input: CareerPlanningInput | None) -> dict:
    if not planning_input:
        return {}
    return {
        key: value
        for key, value in planning_input.model_dump().items()
        if value not in (None, "")
    }


def build_data_source(
    profile: UserProfile,
    tech_record: AssessmentRecord | None,
    planning_input: CareerPlanningInput | None = None,
    general_record: AssessmentRecord | None = None,
) -> RecommendationDataSource:
    fields = []
    field_map = {
        "grade": "年级",
        "major": "专业",
        "interest": "兴趣方向",
        "skills": "已有技能",
        "target_preference": "目标倾向",
        "career_goal": "职业目标",
        "bio": "个人简介",
    }
    for attr, label in field_map.items():
        if getattr(profile, attr, None):
            fields.append(label)

    planning_dict = planning_input_to_dict(planning_input)
    planning_label_map = {
        "school_level": "学校层次",
        "gpa_score": "GPA",
        "rank_level": "专业排名",
        "cet4_score": "英语四级",
        "cet6_score": "英语六级",
        "language_test": "雅思/托福",
        "expected_city": "期望城市",
        "economic_constraint": "经济约束",
        "project_count": "项目数量",
        "project_complexity": "项目复杂度",
        "has_deployment": "是否部署",
        "internship_status": "实习经历",
        "value_preference": "价值偏好",
        "tech_interests": "具体技术兴趣",
        "extra_notes": "补充说明",
    }
    planning_fields = [planning_label_map.get(key, key) for key in planning_dict]

    has_assessment = bool(tech_record and isinstance(tech_record.scores, dict))
    has_general_assessment = bool(general_record and isinstance(general_record.scores, dict))
    base_source = "个人资料、补充规划信息" if planning_fields else "个人资料"
    if has_assessment and has_general_assessment:
        message = f"已使用{base_source}、最近一次计算机能力评估和综合能力评估生成推荐。"
    elif has_assessment:
        message = f"已使用{base_source}和最近一次计算机能力评估生成推荐；综合能力评估可用于补充软能力判断。"
    elif has_general_assessment:
        message = f"已使用{base_source}和综合能力评估生成基础建议；建议再完成计算机能力评估以提升推荐准确度。"
    else:
        message = f"已使用{base_source}生成推荐；尚未检测到能力评估记录，建议先完成综合能力评估和计算机能力评估。"

    return RecommendationDataSource(
        has_profile=True,
        has_assessment=has_assessment,
        has_general_assessment=has_general_assessment,
        assessment_level=tech_record.overall_level if tech_record else None,
        assessment_created_at=tech_record.created_at if tech_record else None,
        general_assessment_level=general_record.overall_level if general_record else None,
        general_assessment_created_at=general_record.created_at if general_record else None,
        profile_fields_used=fields,
        planning_fields_used=planning_fields,
        message=message,
    )


def calc_path_result(profile: UserProfile, db: Session, planning_input: CareerPlanningInput | None = None):
    tech_record = get_latest_assessment_record_by_type(profile.user_id, "tech", db)
    general_record = get_latest_assessment_record_by_type(profile.user_id, "general", db)
    ability = build_ability_from_assessments(tech_record, general_record)

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

    score_map = {}
    path_component_map = {}
    for path_name in ["就业", "考研", "考公", "留学"]:
        components = calc_path_components(path_name, ability_score_map[path_name], profile, planning_input)
        path_component_map[path_name] = components
        score_map[path_name] = components["total"]

    sorted_scores = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
    top_path, top_score = sorted_scores[0]
    second_path, second_score = sorted_scores[1]

    path_reason_map = {
        "就业": "编程实践、项目经历与岗位技能匹配更突出",
        "考研": "编程与算法基础、技术学习能力更适合继续深造",
        "考公": "稳定性、表达能力与信息化岗位适配度更高",
        "留学": "技术学习能力、项目背景与国际化深造需求更接近",
    }

    analysis_text = (
        f"根据你的计算机专业背景、目标偏好与能力画像，当前更适合优先走{top_path}路径。"
        f"你的{path_reason_map[top_path]}；同时，{second_path}路径也具有一定潜力"
        f"（{top_score} vs {second_score}）。"
    )

    if planning_input_to_dict(planning_input):
        analysis_text += " 本次结果已纳入你在 Career 页面补充的成绩、英语、城市、项目、实习和价值偏好信息。"

    return ability, score_map, top_path, analysis_text, path_component_map


def score_career_for_user(
    profile: UserProfile,
    career: Career,
    recommend_path: str,
    ability: dict,
    planning_input: CareerPlanningInput | None = None,
) -> CareerRecommendationItem:
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

    tech_ability_match = calc_career_ability_match(career, ability)
    general_ability_match = calc_career_general_match(career, ability)
    ability_match = blend_career_ability_match(career, tech_ability_match, general_ability_match, ability)
    planning_match = calc_planning_input_career_match(career, planning_input)

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

    score_detail = {
        "专业匹配": round(major_match, 2),
        "技能匹配": round(skill_match, 2),
        "兴趣匹配": round(interest_match, 2),
        "能力匹配": round(ability_match, 2),
        "计算机能力": round(tech_ability_match, 2),
        "补充信息匹配": round(planning_match, 2),
        "路径一致": round(path_match, 2),
    }
    if has_general_assessment(ability):
        score_detail["综合能力"] = round(general_ability_match, 2)

    match_score = clamp_score(
        0.18 * score_detail["专业匹配"]
        + 0.22 * score_detail["技能匹配"]
        + 0.16 * score_detail["兴趣匹配"]
        + 0.18 * score_detail["能力匹配"]
        + 0.18 * score_detail["补充信息匹配"]
        + 0.08 * score_detail["路径一致"]
    )

    reasons = []
    if major_match >= 70:
        reasons.append("专业匹配度较高")
    if skill_match >= 70:
        reasons.append("技能关键词匹配较好")
    if interest_match >= 70:
        reasons.append("兴趣和发展目标较一致")
    if ability_match >= 75:
        reasons.append("能力评估结果支持该方向")
    if has_general_assessment(ability) and general_ability_match >= 75:
        reasons.append("综合能力与该方向要求匹配")
    if planning_match >= 75:
        reasons.append("补充规划信息与该方向匹配")
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
        score_detail=score_detail,
    )


def build_advice_list(recommend_path: str, career_items: List[CareerRecommendationItem]) -> List[str]:
    advice = []

    if recommend_path == "就业":
        advice.extend(
            [
                "建议围绕目标开发方向完成 1 个可运行项目，包含登录、数据库、接口、部署或前后端联调。",
                "同步打磨简历项目描述，突出技术栈、个人负责模块、难点解决和量化结果。",
                "每周保持算法与八股基础训练，优先覆盖数据结构、操作系统、计算机网络和数据库。",
            ]
        )
    elif recommend_path == "考研":
        advice.extend(
            [
                "建议尽快确认目标院校和专业课范围，若考 408，优先拆分数据结构、操作系统、计网和组成原理。",
                "数学与英语要保持长期节奏，专业课每章配套做题和错题复盘。",
                "复试前准备 1 个能讲清楚技术细节的课程项目或科研训练经历。",
            ]
        )
    elif recommend_path == "考公":
        advice.extend(
            [
                "建议优先筛选计算机类、信息化、数字政务、网络安全相关岗位，关注专业限制和基层年限要求。",
                "行测和申论按周训练，同时保留计算机基础、办公自动化和材料写作能力。",
                "项目经历可转化为信息系统维护、数据治理或网络安全管理的岗位表达。",
            ]
        )
    elif recommend_path == "留学":
        advice.extend(
            [
                "建议尽快规划语言成绩、GPA、选校层次和申请方向，明确 CS、SE、DS、AI 或 Security 侧重点。",
                "项目背景要体现代码能力和技术深度，可补充开源、课程设计、科研助理或论文阅读记录。",
                "提前整理英文简历、个人陈述素材和推荐人沟通清单。",
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
        advice.append("建议优先补强这些计算机技能：" + "、".join(unique_gaps[:4]))

    return advice


def split_display_items(text: str | None) -> List[str]:
    return split_keywords(text)[:6]


def grade_stage_label(grade: str | None) -> str:
    grade_text = grade or ""
    if "大一" in grade_text:
        return "基础探索期"
    if "大二" in grade_text:
        return "方向选择期"
    if "大三" in grade_text:
        return "实习/升学冲刺期"
    if "大四" in grade_text:
        return "落地转化期"
    if "研究生" in grade_text:
        return "研究与专业深化期"
    return "阶段待校准"


def build_profile_snapshot(profile: UserProfile, recommend_path: str, career_items: List[CareerRecommendationItem]) -> List[dict]:
    top_career = career_items[0].career_name if career_items else "待生成"
    return [
        {
            "label": "年级阶段",
            "value": profile.grade or "未填写",
            "detail": grade_stage_label(profile.grade),
        },
        {
            "label": "专业方向",
            "value": profile.major or "未填写",
            "detail": "面向计算机、软件工程、人工智能、数据科学、网络安全等方向评估",
        },
        {
            "label": "目标路径",
            "value": normalize_path_preference(profile.target_preference) or recommend_path,
            "detail": f"系统当前推荐优先路径：{recommend_path}",
        },
        {
            "label": "首选方向",
            "value": top_career,
            "detail": "用于承接后续技能差距、项目补强和推荐依据",
        },
    ]


def build_planning_input_snapshot(planning_input: CareerPlanningInput | None) -> List[dict]:
    data = planning_input_to_dict(planning_input)
    items = [
        ("school_level", "学校层次", "未填写"),
        ("gpa_score", "GPA（4.0制）", "未填写"),
        ("rank_level", "专业排名", "未填写"),
        ("cet4_score", "英语四级", "0"),
        ("cet6_score", "英语六级", "0"),
        ("language_test", "雅思/托福", "未填写"),
        ("expected_city", "期望城市", "未填写"),
        ("economic_constraint", "经济约束", "未填写"),
        ("project_count", "项目数量", "0"),
        ("project_complexity", "项目复杂度", "未填写"),
        ("internship_status", "实习经历", "未填写"),
        ("value_preference", "价值偏好", "未填写"),
    ]
    return [
        {
            "label": label,
            "value": str(data.get(key, empty)),
        }
        for key, label, empty in items
    ]


def build_ability_breakdown(ability: dict) -> List[dict]:
    tech_scores = ability.get("tech_scores") if isinstance(ability.get("tech_scores"), dict) else {}
    if tech_scores and any(key in tech_scores for key in ["programming", "algorithm", "computer_basic"]):
        ability_meta = {
            "programming": {
                "label": "编程能力",
                "covers": ["主语言", "面向对象", "函数抽象", "代码实现"],
                "suggestion": "选择 Python/Java/C++/Go 中一门作为主语言，完成一个可运行项目。",
            },
            "algorithm": {
                "label": "数据结构与算法",
                "covers": ["数组链表", "树图", "复杂度", "中等题"],
                "suggestion": "从 LeetCode Hot 100 和数据结构高频题开始，固定节奏刷题复盘。",
            },
            "computer_basic": {
                "label": "计算机基础",
                "covers": ["操作系统", "网络协议", "组成原理", "核心概念"],
                "suggestion": "围绕操作系统、计网、数据库和组成原理建立面试笔记。",
            },
            "software_eng": {
                "label": "软件工程",
                "covers": ["Git", "测试", "敏捷流程", "协作规范"],
                "suggestion": "把项目补上版本管理、测试、README、接口文档和代码规范。",
            },
            "backend": {
                "label": "后端开发",
                "covers": ["框架", "接口", "数据库交互", "微服务"],
                "suggestion": "用 Spring Boot/FastAPI/Express 完成鉴权、日志、数据库和接口模块。",
            },
            "frontend": {
                "label": "前端开发",
                "covers": ["Vue/React", "JS/TS", "路由状态", "工程化"],
                "suggestion": "做一个组件化前端项目，补充接口联调、状态管理和移动端适配。",
            },
            "database": {
                "label": "数据库",
                "covers": ["SQL", "索引事务", "NoSQL", "表设计"],
                "suggestion": "练习复杂查询、索引设计、事务隔离和 Redis/MongoDB 常见场景。",
            },
            "network": {
                "label": "计算机网络",
                "covers": ["HTTP", "TCP/IP", "DNS", "Web安全"],
                "suggestion": "补 HTTP、TCP、DNS、CDN、负载均衡和常见 Web 安全问题。",
            },
            "ai_ml": {
                "label": "AI与机器学习",
                "covers": ["机器学习", "深度学习", "PyTorch", "大模型应用"],
                "suggestion": "用 Python 完成模型调用、数据处理或 RAG/知识库问答小项目。",
            },
            "devops": {
                "label": "运维与部署",
                "covers": ["Linux", "Shell", "Docker", "云服务"],
                "suggestion": "把现有项目部署到云服务器或平台，补充 Docker 和 CI/CD 记录。",
            },
        }
        source_scores = tech_scores
    elif not tech_scores:
        return []
    else:
        ability_meta = {
            "logic": {
                "label": "编程与算法",
                "covers": ["语言基础", "数据结构", "复杂度分析", "算法题表达"],
                "suggestion": "用固定语言完成数组、链表、树、图和动态规划的高频题型训练。",
            },
            "innovation": {
                "label": "项目工程",
                "covers": ["项目拆解", "接口设计", "数据库建模", "部署上线"],
                "suggestion": "把课程练习升级为可运行项目，补充异常处理、日志、权限和部署说明。",
            },
            "communication": {
                "label": "项目表达",
                "covers": ["技术表达", "文档说明", "团队协作", "面试讲项目"],
                "suggestion": "用 STAR 结构整理项目：目标、技术方案、负责模块、难点和结果。",
            },
            "learning": {
                "label": "计算机基础",
                "covers": ["文档阅读", "新框架上手", "持续复盘", "英语资料"],
                "suggestion": "围绕目标岗位建立每周学习闭环：输入、练习、输出、复盘。",
            },
            "pressure": {
                "label": "调试排错",
                "covers": ["报错定位", "问题拆解", "联调排查", "面试压力"],
                "suggestion": "记录常见 bug、定位过程和解决方案，形成自己的排错清单。",
            },
            "leadership": {
                "label": "规划执行",
                "covers": ["方向选择", "任务拆解", "优先级", "长期路线"],
                "suggestion": "把目标拆成课程基础、项目作品、实习/升学材料三个层级推进。",
            },
        }
        source_scores = ability

    result = []
    for key, meta in ability_meta.items():
        score = float(source_scores.get(key, 0))
        if score >= 80:
            level = "优势"
        elif score >= 65:
            level = "可用"
        else:
            level = "需补强"
        result.append(
            {
                "key": key,
                "label": meta["label"],
                "score": round(score, 1),
                "level": level,
                "covers": meta["covers"],
                "suggestion": meta["suggestion"],
            }
        )
    return result


def build_computer_planning(
    profile: UserProfile,
    ability: dict,
    recommend_path: str,
    career_items: List[CareerRecommendationItem],
    planning_input: CareerPlanningInput | None = None,
) -> dict:
    all_gaps = []
    for item in career_items:
        for gap in item.gap_skills:
            if gap and gap not in all_gaps:
                all_gaps.append(gap)

    return {
        "profile_snapshot": build_profile_snapshot(profile, recommend_path, career_items),
        "planning_input_snapshot": build_planning_input_snapshot(planning_input),
        "ability_breakdown": build_ability_breakdown(ability),
        "interest_values": [
            {
                "label": "兴趣方向",
                "items": split_display_items(profile.interest),
                "empty": "建议填写后端、前端、AI、数据、安全、嵌入式、产品等具体兴趣",
            },
            {
                "label": "已有技能",
                "items": split_display_items(profile.skills),
                "empty": "建议填写 Python、Java、C++、Vue、MySQL、Linux、Git 等技能",
            },
            {
                "label": "职业目标",
                "items": split_display_items(profile.career_goal),
                "empty": "建议写清目标岗位、城市、读研/就业倾向和时间节点",
            },
        ],
        "priority_tasks": [
            f"优先补强 {skill}" for skill in all_gaps[:3]
        ] or ["补充一个可运行项目并整理项目说明", "完善个人资料后重新生成推荐", "用能力评估定位技术短板"],
    }


def upsert_default_careers(db: Session) -> dict:
    inserted = 0
    updated = 0
    for item in DEFAULT_CAREERS:
        existing = db.query(Career).filter(Career.career_name == item["career_name"]).first()
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
            updated += 1
            continue
        db.add(Career(**item))
        inserted += 1

    if inserted or updated:
        db.commit()
    return {"inserted": inserted, "updated": updated}


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
    result = upsert_default_careers(db)
    return {"message": f"默认职业库初始化完成，本次新增 {result['inserted']} 条数据，更新 {result['updated']} 条数据"}


@router.get("/recommendation/{user_id}", response_model=CareerRecommendationResponse)
def get_career_recommendation(user_id: int, db: Session = Depends(get_db)):
    return build_career_recommendation(user_id=user_id, planning_input=None, db=db)


@router.post("/recommendation/{user_id}", response_model=CareerRecommendationResponse)
def post_career_recommendation(
    user_id: int,
    planning_input: CareerPlanningInput = Body(default_factory=CareerPlanningInput),
    db: Session = Depends(get_db),
):
    return build_career_recommendation(user_id=user_id, planning_input=planning_input, db=db)


def build_career_recommendation(
    user_id: int,
    planning_input: CareerPlanningInput | None,
    db: Session,
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先完善个人信息后再生成职业发展推荐")

    upsert_default_careers(db)

    ability_snapshot_dict, score_map, recommend_path, analysis_text, path_component_map = calc_path_result(profile, db, planning_input)

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

    tech_record = get_latest_assessment_record_by_type(user_id, "tech", db)
    general_record = get_latest_assessment_record_by_type(user_id, "general", db)
    data_source = build_data_source(profile, tech_record, planning_input, general_record)

    scored_items = [
        score_career_for_user(profile, career, recommend_path, ability_snapshot_dict, planning_input)
        for career in candidate_careers
    ]
    scored_items.sort(key=lambda x: x.match_score, reverse=True)
    career_list = scored_items[:3]

    advice_list = build_advice_list(recommend_path, career_list)
    computer_planning = build_computer_planning(profile, ability_snapshot_dict, recommend_path, career_list, planning_input)
    computer_planning["path_score_detail"] = path_component_map

    ability_snapshot = AbilitySnapshot(**ability_snapshot_dict)

    return CareerRecommendationResponse(
        user_id=user_id,
        ability_snapshot=ability_snapshot,
        data_source=data_source,
        path_result=path_record,
        career_list=career_list,
        advice_list=advice_list,
        computer_planning=computer_planning,
    )


@router.get("/recommend/{user_id}", response_model=List[CareerResponse])
def recommend_careers(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先完善个人信息")

    upsert_default_careers(db)

    ability_snapshot_dict, score_map, recommend_path, analysis_text, _ = calc_path_result(profile, db)

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
        .all()
    )

    if careers:
        scored_items = [
        score_career_for_user(profile, career, recommend_path, ability_snapshot_dict, None)
            for career in careers
        ]
        scored_items.sort(key=lambda x: x.match_score, reverse=True)
        career_ids = [item.career_id for item in scored_items[:3]]
        return [career for career in careers if career.career_id in career_ids]

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
