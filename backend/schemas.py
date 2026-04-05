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