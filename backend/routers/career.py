from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Career, CareerPath, UserProfile
from schemas import CareerCreate, CareerUpdate, CareerResponse

router = APIRouter()


@router.get("/", response_model=List[CareerResponse])
def get_all_careers(db: Session = Depends(get_db)):
    return db.query(Career).filter(Career.is_active == True).all()


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


@router.get("/recommend/{user_id}", response_model=List[CareerResponse])
def recommend_careers(user_id: int, db: Session = Depends(get_db)):
    path = db.query(CareerPath).filter(CareerPath.user_id == user_id).first()
    if not path:
        raise HTTPException(status_code=404, detail="请先生成发展路径推荐结果")

    # 先做最简推荐：如果推荐路径不是就业，先返回对应路径下的职业
    careers = db.query(Career).filter(
        Career.recommend_path == path.recommend_path,
        Career.is_active == True
    ).limit(3).all()

    if careers:
        return careers

    # 如果没有匹配到，再兜底返回3个职业
    return db.query(Career).filter(Career.is_active == True).limit(3).all()