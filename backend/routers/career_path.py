from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import CareerPath, User
from schemas import CareerPathCreate, CareerPathUpdate, CareerPathResponse

router = APIRouter()


@router.get("/{user_id}", response_model=CareerPathResponse)
def get_career_path(user_id: int, db: Session = Depends(get_db)):
    career_path = db.query(CareerPath).filter(CareerPath.user_id == user_id).first()
    if not career_path:
        raise HTTPException(status_code=404, detail="该用户还没有发展路径推荐记录")
    return career_path


@router.post("/", response_model=CareerPathResponse)
def create_career_path(path_data: CareerPathCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == path_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing = db.query(CareerPath).filter(CareerPath.user_id == path_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该用户的路径推荐记录已存在")

    new_path = CareerPath(**path_data.model_dump())
    db.add(new_path)
    db.commit()
    db.refresh(new_path)
    return new_path


@router.put("/{user_id}", response_model=CareerPathResponse)
def update_career_path(user_id: int, path_data: CareerPathUpdate, db: Session = Depends(get_db)):
    career_path = db.query(CareerPath).filter(CareerPath.user_id == user_id).first()
    if not career_path:
        raise HTTPException(status_code=404, detail="该用户还没有发展路径推荐记录")

    update_data = path_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(career_path, key, value)

    db.commit()
    db.refresh(career_path)
    return career_path