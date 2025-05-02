# cycles.py
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Cycle, Envelope, Category

router = APIRouter(prefix="/cycles", tags=["Cycles"])

@router.post("/", response_model=Cycle)
def create_cycle(cycle: Cycle, session: Session = Depends(get_session)):
    """
    Create a new pay period (Cycle), automatically create envelopes for each category.
    We do half-budget logic if it's the first cycle in a given month vs. second cycle.
    If there's overspend from the first cycle, we reduce the second cycle envelopes 
    accordingly, except for "Rent" which is untouchable.
    """
    # 1) Insert the cycle
    session.add(cycle)
    session.commit()
    session.refresh(cycle)

    # 2) Get all categories
    statement = select(Category)
    categories = session.exec(statement).all()

    # 3) Determine if there is an existing cycle in the same month/year (the "first" cycle)
    #    We'll do a naive approach: filter cycles by year/month
    month = cycle.start_date.month
    year = cycle.start_date.year

    # Query for any other cycle in the same month/year
    stmt_existing = select(Cycle).where(
        (Cycle.id != cycle.id) &
        (Cycle.start_date.month == month) &
        (Cycle.start_date.year == year)
    )
    first_cycle_in_month = session.exec(stmt_existing).first()

    if not first_cycle_in_month:
        # This is the FIRST cycle in the month:
        # - envelopes start with half of each category's monthly budget
        for cat in categories:
            half = cat.monthly_budget / Decimal("2")
            envelope = Envelope(
                cycle_id=cycle.id,
                category_id=cat.id,
                initial=half,
                current=half
            )
            session.add(envelope)
    else:
        # This is the SECOND cycle in the month
        # 1) For each category:
        #    half = cat.monthly_budget / 2
        #    base_allocation = half
        # 2) Check the first cycle's envelope. If overspent (envelope.current < 0), 
        #    we reduce the second cycle's envelope by that negative amount 
        #    except for rent.
        #    i.e. new_envelope.initial = half - (abs(overspent)) if not rent
        #    if rent, we do NOT reduce it.
        # 3) new_envelope.current = new_envelope.initial
        for cat in categories:
            half = cat.monthly_budget / Decimal("2")
            new_envelope_allocation = half

            # Find the envelope for 'first_cycle_in_month' for this category
            stmt_env = select(Envelope).where(
                (Envelope.cycle_id == first_cycle_in_month.id) &
                (Envelope.category_id == cat.id)
            )
            old_envelope = session.exec(stmt_env).first()

            if old_envelope and old_envelope.current < 0:
                overspent = abs(old_envelope.current)
                if cat.name.lower() != "rent":  # if not rent, reduce second half
                    new_envelope_allocation = new_envelope_allocation - overspent
                    if new_envelope_allocation < 0:
                        new_envelope_allocation = Decimal("0.00")

            envelope = Envelope(
                cycle_id=cycle.id,
                category_id=cat.id,
                initial=new_envelope_allocation,
                current=new_envelope_allocation
            )
            session.add(envelope)

    session.commit()
    session.refresh(cycle)
    return cycle

@router.get("/", response_model=list[Cycle])
def get_cycles(session: Session = Depends(get_session)):
    """
    List all cycles (pay periods).
    """
    statement = select(Cycle)
    cycles = session.exec(statement).all()
    return cycles

@router.delete("/{cycle_id}")
def delete_cycle(cycle_id: int, session: Session = Depends(get_session)):
    """
    Delete a cycle by ID, cascade-delete envelopes & transactions.
    """
    cycle = session.get(Cycle, cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found.")

    # Because we have relationships, if we want automatic cascade we can
    # rely on constraints, or simply delete them in Python:
    # But for simplicity, let's just do session.delete(cycle).
    session.delete(cycle)
    session.commit()
    return {"ok": True, "message": "Cycle deleted."}
