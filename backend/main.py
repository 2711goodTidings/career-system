import os
import shutil
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, User, UserProfile
from schemas import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)

app = FastAPI(title="Career Planner API")

# 自动建表
Base.metadata.create_all(bind=engine)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传目录
UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 静态资源挂载
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ========= 基础接口 =========
@app.get("/")
def root():
    return {"message": "Career Planner backend is running"}


# ========= 注册登录模块（队友写这里） =========
@app.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=user_data.username,
        password=user_data.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == user_data.username,
        User.password == user_data.password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {
        "message": "登录成功",
        "user_id": user.user_id,
        "username": user.username
    }


# ========= 个人信息模块（你写这里） =========
@app.get("/profile/{user_id}", response_model=UserProfileResponse)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="该用户还没有个人信息记录")

    return profile


@app.post("/profile", response_model=UserProfileResponse)
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
        major=profile_data.major,
        grade=profile_data.grade,
        age=profile_data.age,
        phone=profile_data.phone,
        email=profile_data.email,
        bio=profile_data.bio
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@app.put("/profile/{user_id}", response_model=UserProfileResponse)
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


@app.post("/upload-avatar/{user_id}")
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