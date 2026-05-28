from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ========= 用户认证相关 =========
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# ========= 用户个人信息相关 =========
class UserProfileBase(BaseModel):
    real_name: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    interest: Optional[str] = None
    skills: Optional[str] = None
    target_preference: Optional[str] = None
    career_goal: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    """创建个人资料"""
    user_id: int

class UserProfileUpdate(UserProfileBase):
    """更新个人资料"""
    pass

class UserProfileResponse(UserProfileBase):
    profile_id: int
    user_id: int
    avatar: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# ========= 能力评估相关 =========
class AssessmentQuestionResponse(BaseModel):
    id: int
    dimension: str
    question_text: str
    order_num: int

    class Config:
        from_attributes = True

class AssessmentSubmit(BaseModel):
    answers: Dict[int, int]  # {question_id: score}

class AssessmentResultResponse(BaseModel):
    scores: Dict[str, float]
    overall_level: str
    suggestions: str
    radar_data: Dict[str, float]
    created_at: datetime

class AssessmentHistoryResponse(BaseModel):
    id: int
    scores: Dict[str, float]
    overall_level: str
    created_at: datetime

    class Config:
        from_attributes = True

# ========= 发展路径相关 =========
class CareerPathBase(BaseModel):
    job_score: Optional[float] = 0.0
    graduate_score: Optional[float] = 0.0
    civil_service_score: Optional[float] = 0.0
    abroad_score: Optional[float] = 0.0
    recommend_path: Optional[str] = None
    analysis_text: Optional[str] = None

class CareerPathCreate(CareerPathBase):
    pass

class CareerPathUpdate(CareerPathBase):
    pass

class CareerPathResponse(CareerPathBase):
    path_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ========= 职业相关 =========
class CareerBase(BaseModel):
    career_name: str
    category: Optional[str] = None
    industry: Optional[str] = None
    education_require: Optional[str] = None
    avg_salary: Optional[int] = None
    growth_potential: Optional[str] = None
    suitable_major: Optional[str] = None
    suitable_skills: Optional[str] = None
    skill_require: Optional[str] = None
    description: Optional[str] = None
    work_content: Optional[str] = None
    recommend_path: Optional[str] = "就业"
    is_active: Optional[bool] = True

class CareerCreate(CareerBase):
    pass

class CareerUpdate(CareerBase):
    pass

class CareerResponse(CareerBase):
    career_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ========= 综合职业发展推荐返回 =========
class AbilitySnapshot(BaseModel):
    logic: float
    innovation: float
    communication: float
    learning: float
    pressure: float
    leadership: float
    tech_scores: Dict[str, float] = Field(default_factory=dict)
    general_scores: Dict[str, float] = Field(default_factory=dict)


class RecommendationDataSource(BaseModel):
    has_profile: bool = True
    has_assessment: bool = False
    has_general_assessment: bool = False
    assessment_level: Optional[str] = None
    assessment_created_at: Optional[datetime] = None
    general_assessment_level: Optional[str] = None
    general_assessment_created_at: Optional[datetime] = None
    profile_fields_used: List[str] = Field(default_factory=list)
    planning_fields_used: List[str] = Field(default_factory=list)
    message: str = ""


class CareerPlanningInput(BaseModel):
    school_level: Optional[str] = None
    gpa_score: Optional[float] = None
    rank_level: Optional[str] = None
    cet4_score: Optional[int] = 0
    cet6_score: Optional[int] = 0
    language_test: Optional[str] = None
    expected_city: Optional[str] = None
    economic_constraint: Optional[str] = None
    project_count: Optional[int] = 0
    project_complexity: Optional[str] = None
    has_deployment: Optional[str] = None
    internship_status: Optional[str] = None
    value_preference: Optional[str] = None
    tech_interests: Optional[str] = None
    extra_notes: Optional[str] = None


class CareerRecommendationItem(BaseModel):
    career_id: int
    career_name: str
    category: Optional[str] = None
    industry: Optional[str] = None
    education_require: Optional[str] = None
    avg_salary: Optional[int] = None
    growth_potential: Optional[str] = None
    suitable_major: Optional[str] = None
    suitable_skills: Optional[str] = None
    skill_require: Optional[str] = None
    description: Optional[str] = None
    work_content: Optional[str] = None
    recommend_path: Optional[str] = None
    is_active: bool

    match_score: float
    reasons: List[str] = Field(default_factory=list)
    gap_skills: List[str] = Field(default_factory=list)
    score_detail: Dict[str, float] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class CareerRecommendationResponse(BaseModel):
    user_id: int
    ability_snapshot: AbilitySnapshot
    data_source: RecommendationDataSource = Field(default_factory=RecommendationDataSource)
    path_result: CareerPathResponse
    career_list: List[CareerRecommendationItem]
    advice_list: List[str] = Field(default_factory=list)
    computer_planning: Dict[str, Any] = Field(default_factory=dict)

# ========= AI 职业规划问答 =========
class PlanningChatRequest(BaseModel):
    user_id: int
    question: str


class PlanningYearlyPlanRequest(BaseModel):
    user_id: int
    selected_path: Optional[str] = None


class PlanningChatResponse(BaseModel):
    answer: str = ""
    provider: str = ""
    model: str = ""
    success: bool
    error: Optional[str] = None
    from_cache: bool = False
    created_at: Optional[datetime] = None

# ========= 通用响应 =========
class MessageResponse(BaseModel):
    message: str
    success: bool = True
