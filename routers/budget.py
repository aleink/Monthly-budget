from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from decimal import Decimal

from database import get_session
from models import Cycle, Envelope, Category

router = APIRouter(prefix="/budget", tags=["Budget"])

@router.get("/")
def get_current_budget(session: Session = Depends(get_session)):
    # find the most recent cycle
    stmt_cycle = select(Cycle).order_by(Cycle.start_date.desc())
    latest_cycle = session.exec(stmt_cycle).first()
    if not latest_cycle:
        return {"message": "No cycles available."}

    stmt_env = (
        select(Envelope, Category)
        .join(Category, Envelope.category_id == Category.id)
        .where(Envelope.cycle_id == latest_cycle.id)
    )
    results = session.exec(stmt_env).all()

    envelopes_data = []
    for (env, cat) in results:
        if env.initial == Decimal("0.00"):
            pct = 0
        else:
            pct = (env.current / env.initial) * Decimal("100.00")

        envelopes_data.append({
            "category": cat.name,
            "initial": str(env.initial),
            "remaining": str(env.current),
            "percentage_left": f"{pct:.2f}%"
        })

    return {
        "cycle_id": latest_cycle.id,
        "start_date": str(latest_cycle.start_date),
        "envelopes": envelopes_data
    }
