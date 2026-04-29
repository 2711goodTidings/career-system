from typing import Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# ========= 用户认证相关 =========
class UserRegister(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: Optional[str] = None
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
    pass

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
    communication: float
    execution: float
    research: float
    stability: float
    english: float
    skill_practice: float
    adaptability: float


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

    model_config = ConfigDict(from_attributes=True)


class CareerRecommendationResponse(BaseModel):
    user_id: int
    ability_snapshot: AbilitySnapshot
    path_result: CareerPathResponse
    career_list: List[CareerRecommendationItem]
    advice_list: List[str] = Field(default_factory=list)

# ========= 通用响应 =========
class MessageResponse(BaseModel):
    message: str
    success: bool = True
