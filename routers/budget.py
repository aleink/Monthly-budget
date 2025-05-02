# routers/budget.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from models import Cashflow, Category

router = APIRouter(prefix="/budget", tags=["Budget"])

@router.get("/")
def get_budget(session: Session = Depends(get_session)):
    cf = session.get(Cashflow, 1)
    if not cf:
        return {"message": "Cashflow record missing"}
    stmt = select(Category)
    cats = session.exec(stmt).all()
    cat_list = []
    for c in cats:
        cat_list.append({
            "id": c.id,
            "name": c.name,
            "is_rent": c.is_rent,
            "biweekly_budget": str(c.biweekly_budget),
            "monthly_budget": str(c.monthly_budget),
            "current_envelope": str(c.current_envelope)
        })
    return {
        "available_cash": str(cf.balance),
        "categories": cat_list
    }
