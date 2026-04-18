import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserProfile
from schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)

router = APIRouter()

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/{user_id}", response_model=UserProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="该用户还没有个人信息记录")

    return profile


@router.post("/", response_model=UserProfileResponse)
def create_profile(profile_data: UserProfileCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == profile_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在，请先注册")

    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == profile_data.user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="该用户个人信息已存在，请使用修改接口")

    new_profile = UserProfile(
        user_id=profile_data.user_id,
        real_name=profile_data.real_name,
        gender=profile_data.gender,
        school=profile_data.school,
        major=profile_data.major,
        grade=profile_data.grade,
        age=profile_data.age,
        phone=profile_data.phone,
        email=profile_data.email,
        bio=profile_data.bio,

        # ===== 新增字段 =====
        interest=profile_data.interest,
        skills=profile_data.skills,
        target_preference=profile_data.target_preference,
        career_goal=profile_data.career_goal
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.put("/{user_id}", response_model=UserProfileResponse)
def update_profile(user_id: int, profile_data: UserProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="该用户还没有个人信息，请先创建")

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/upload-avatar/{user_id}")
def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="请先创建个人信息，再上传头像")

    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 jpg、jpeg、png、webp 图片")

    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"user_{user_id}_{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    avatar_url = f"/uploads/avatars/{unique_filename}"
    profile.avatar = avatar_url
    db.commit()
    db.refresh(profile)

    return {
        "message": "头像上传成功",
        "avatar_url": avatar_url
    }