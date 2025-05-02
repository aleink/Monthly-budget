# categories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlmodel import Session

from database import get_session
from models import Category

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session)):
    """
    Create a new category. 
    Expects a Category object with 'name' and 'monthly_budget'.
    """
    # Check if a category with this name already exists (optional check)
    statement = select(Category).where(Category.name == category.name)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists.")

    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/", response_model=list[Category])
def get_categories(session: Session = Depends(get_session)):
    """
    List all categories.
    """
    statement = select(Category)
    results = session.exec(statement).all()
    return results

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    """
    Delete a category by ID.
    """
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    session.delete(category)
    session.commit()
    return {"ok": True, "message": "Category deleted."}
