from typing import Optional
from pydantic import BaseModel, ConfigDict


# ========= 注册登录模块 =========
class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


# ========= 个人信息模块 =========
class UserProfileCreate(BaseModel):
    user_id: int
    real_name: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None


class UserProfileUpdate(BaseModel):
    real_name: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None


class UserProfileResponse(BaseModel):
    profile_id: int
    user_id: int
    avatar: Optional[str] = None
    real_name: Optional[str] = None
    gender: Optional[str] = None
    school: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
# ========= 发展路径推荐模块 =========
class CareerPathCreate(BaseModel):
    user_id: int
    job_score: float = 0.0
    graduate_score: float = 0.0
    civil_service_score: float = 0.0
    abroad_score: float = 0.0
    recommend_path: str
    analysis_text: Optional[str] = None


class CareerPathUpdate(BaseModel):
    job_score: Optional[float] = None
    graduate_score: Optional[float] = None
    civil_service_score: Optional[float] = None
    abroad_score: Optional[float] = None
    recommend_path: Optional[str] = None
    analysis_text: Optional[str] = None


class CareerPathResponse(BaseModel):
    path_id: int
    user_id: int
    job_score: float
    graduate_score: float
    civil_service_score: float
    abroad_score: float
    recommend_path: str
    analysis_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ========= 职业推荐模块 =========
class CareerCreate(BaseModel):
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


class CareerUpdate(BaseModel):
    career_name: Optional[str] = None
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
    is_active: Optional[bool] = None


class CareerResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)