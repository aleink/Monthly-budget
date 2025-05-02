# cycles.py
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Cycle, Envelope, Category
from schemas import CycleCreate, CycleRead

router = APIRouter(prefix="/cycles", tags=["Cycles"])

@router.post("/", response_model=CycleRead)
def create_cycle(data: CycleCreate, session: Session = Depends(get_session)):
    # data.start_date is a python date already
    cycle = Cycle(pay_amount=data.pay_amount, start_date=data.start_date)
    session.add(cycle)
    session.commit()
    session.refresh(cycle)

    # Grab all categories
    all_cats = session.exec(select(Category)).all()

    month = data.start_date.month
    year = data.start_date.year

    # fetch all existing cycles
    existing_cycles = session.exec(select(Cycle)).all()
    # find if there's a first cycle in the same month/year
    first_cycle_in_month = None
    for c in existing_cycles:
        if c.id != cycle.id and c.start_date.month == month and c.start_date.year == year:
            first_cycle_in_month = c
            break

    if not first_cycle_in_month:
        # FIRST cycle in the month
        for cat in all_cats:
            half = cat.monthly_budget / Decimal("2.0")
            env = Envelope(
                cycle_id=cycle.id,
                category_id=cat.id,
                initial=half,
                current=half,
            )
            session.add(env)
    else:
        # SECOND cycle in the month
        for cat in all_cats:
            half = cat.monthly_budget / Decimal("2.0")
            new_allocation = half

            # find envelope from the first cycle
            stmt_env = select(Envelope).where(
                (Envelope.cycle_id == first_cycle_in_month.id)
                & (Envelope.category_id == cat.id)
            )
            old_env = session.exec(stmt_env).first()
            if old_env and old_env.current < 0:
                overspent = abs(old_env.current)
                if cat.name.lower() != "rent":
                    new_allocation -= overspent
                    if new_allocation < 0:
                        new_allocation = Decimal("0.00")

            env = Envelope(
                cycle_id=cycle.id,
                category_id=cat.id,
                initial=new_allocation,
                current=new_allocation,
            )
            session.add(env)

    session.commit()
    session.refresh(cycle)
    return cycle

@router.get("/", response_model=list[CycleRead])
def get_cycles(session: Session = Depends(get_session)):
    stmt = select(Cycle)
    return session.exec(stmt).all()

@router.delete("/{cycle_id}")
def delete_cycle(cycle_id: int, session: Session = Depends(get_session)):
    cyc = session.get(Cycle, cycle_id)
    if not cyc:
        raise HTTPException(status_code=404, detail="Cycle not found.")
    session.delete(cyc)
    session.commit()
    return {"ok": True, "message": "Cycle deleted."}
