# routers/categories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Category
from schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    stmt = select(Category).where(Category.name == data.name)
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name exists.")
    cat = Category(
        name=data.name,
        is_rent=data.is_rent,
        biweekly_budget=data.biweekly_budget,
        monthly_budget=data.monthly_budget,
        current_envelope=0
    )
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat

@router.get("/", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    cats = session.exec(select(Category)).all()
    return cats

@router.delete("/{cat_id}")
def delete_category(cat_id: int, session: Session = Depends(get_session)):
    cat = session.get(Category, cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Not found.")
    session.delete(cat)
    session.commit()
    return {"ok": True}
