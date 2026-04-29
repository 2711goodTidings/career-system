import datetime 
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.types import JSON 


# ========= 用户表 =========
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    assessment_records = relationship("AssessmentRecord", back_populates="user")

# ========= 用户个人信息表 =========
class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)

    avatar = Column(String(255), nullable=True)
    real_name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)
    school = Column(String(100), nullable=True)
    major = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)

    # ===== 新增字段 =====
    interest = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    target_preference = Column(String(20), nullable=True)
    career_goal = Column(String(255), nullable=True)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")

# ========= 能力评估表 =========
class AssessmentQuestion(Base):
    """评估题目表"""
    __tablename__ = "assessment_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    dimension = Column(String(50), nullable=False)  # 所属维度：logic, innovation, communication, learning, pressure, leadership
    question_text = Column(String(500), nullable=False)  # 题目内容
    order_num = Column(Integer, default=0)  # 排序

class AssessmentRecord(Base):
    __tablename__ = "assessment_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))  # 改为 user_id
    scores = Column(JSON)
    answers = Column(JSON)
    overall_level = Column(String(20))
    suggestions = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    
    # 关联用户
    user = relationship("User", back_populates="assessment_records")

# ========= 发展路径推荐表 =========
class CareerPath(Base):
    __tablename__ = "career_paths"

    path_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)

    job_score = Column(Float, default=0.0)
    graduate_score = Column(Float, default=0.0)
    civil_service_score = Column(Float, default=0.0)
    abroad_score = Column(Float, default=0.0)

    recommend_path = Column(String(20), nullable=False)
    analysis_text = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# ========= 职业库表 =========
class Career(Base):
    __tablename__ = "careers"

    career_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    career_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    education_require = Column(String(100), nullable=True)
    avg_salary = Column(Integer, nullable=True)
    growth_potential = Column(String(50), nullable=True)

    suitable_major = Column(String(255), nullable=True)
    suitable_skills = Column(Text, nullable=True)
    skill_require = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    work_content = Column(Text, nullable=True)

    recommend_path = Column(String(20), default="就业")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())