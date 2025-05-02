from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Category
from schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)):
    # optional check for duplicate name
    stmt = select(Category).where(Category.name == data.name)
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists.")

    new_cat = Category(
        name=data.name,
        monthly_budget=data.monthly_budget
    )
    session.add(new_cat)
    session.commit()
    session.refresh(new_cat)
    return new_cat

@router.get("/", response_model=list[CategoryRead])
def get_categories(session: Session = Depends(get_session)):
    stmt = select(Category)
    results = session.exec(stmt).all()
    # Because we have `orm_mode=True`, we can return `results` directly
    return results

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    cat = session.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    session.delete(cat)
    session.commit()
    return {"ok": True, "message": "Category deleted."}
