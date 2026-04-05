from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base


# ========= 用户表 =========
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False)


# ========= 用户个人信息表 =========
class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)

    avatar = Column(String(255), nullable=True)
    real_name = Column(String(50), nullable=True)
    gender = Column(String(10), nullable=True)
    major = Column(String(100), nullable=True)
    grade = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")