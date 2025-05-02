# routers/transactions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Transaction, Cashflow, Category, TxType
from schemas import TransactionCreate, TransactionRead
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionRead)
def create_transaction(data: TransactionCreate, session: Session = Depends(get_session)):
    cf = session.get(Cashflow, 1)
    if not cf:
        cf = Cashflow(id=1, balance=Decimal("0.00"))
        session.add(cf)
        session.commit()
        session.refresh(cf)

    txn = Transaction(
        amount=data.amount,
        type=data.type,
        category_id=data.category_id
    )

    # We'll assume "today" for logic. Optionally let user pass a date.
    today = datetime.utcnow()

    if data.type == TxType.paycheck:
        # 1) add to available cash
        cf.balance += data.amount

        # 2) move leftover from non-rent categories to available, then reset them
        #    for rent categories, keep leftover, just add half monthly rent
        cats = session.exec(select(Category)).all()
        for cat in cats:
            if cat.is_rent:
                # add half of monthly rent to that envelope
                # (If user wants the exact half = monthly_budget/2, do so)
                half = cat.monthly_budget / Decimal("2.0")
                cat.current_envelope += half
            else:
                # leftover -> available
                leftover = cat.current_envelope
                cf.balance += leftover
                # reset to the biweekly budget
                cat.current_envelope = cat.biweekly_budget
            session.add(cat)

    elif data.type == TxType.atm:
        cf.balance += data.amount

    elif data.type == TxType.expense:
        if not data.category_id:
            raise HTTPException(400, "Category required for expense.")
        cat = session.get(Category, data.category_id)
        if not cat:
            raise HTTPException(404, "Category not found.")
        # subtract from available AND from envelope
        if cf.balance < data.amount:
            # optional: allow negative or raise
            pass
        cf.balance -= data.amount
        if cat.current_envelope < data.amount:
            # If envelope doesn't have enough, either go negative
            # or just let the user do partial from envelope, partial from CF
            pass
        cat.current_envelope -= data.amount
        session.add(cat)

    elif data.type == TxType.rent_expense:
        # Subtract from available + rent envelope
        # Usually you'd have exactly 1 rent category. Let's find it:
        stmt = select(Category).where(Category.is_rent == True)
        rent_cat = session.exec(stmt).first()
        if not rent_cat:
            raise HTTPException(400, "No rent category defined.")
        cf.balance -= data.amount
        rent_cat.current_envelope -= data.amount
        session.add(rent_cat)

    else:
        raise HTTPException(400, "Unsupported transaction type.")

    session.add(cf)
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn

@router.get("/", response_model=list[TransactionRead])
def list_transactions(session: Session = Depends(get_session)):
    stmt = select(Transaction).order_by(Transaction.timestamp.desc())
    txns = session.exec(stmt).all()
    return txns

@router.delete("/{txn_id}")
def delete_transaction(txn_id: int, session: Session = Depends(get_session)):
    """
    Basic revert:
    - If it's a paycheck, subtract from CF
      (We won't re-revert the leftover logic or envelope resets, to keep it simpler.)
    - If ATM, subtract from CF
    - If expense or rent_expense, add back to CF/envelope
    """
    txn = session.get(Transaction, txn_id)
    if not txn:
        raise HTTPException(404, "Not found.")
    cf = session.get(Cashflow, 1)
    if not cf:
        raise HTTPException(500, "Cashflow missing?")

    if txn.type == TxType.paycheck:
        cf.balance -= txn.amount
        # not resetting envelopes to old states, that gets complicated
    elif txn.type == TxType.atm:
        cf.balance -= txn.amount
    elif txn.type == TxType.expense:
        cat = session.get(Category, txn.category_id)
        if cat:
            cat.current_envelope += txn.amount
            session.add(cat)
        cf.balance += txn.amount
    elif txn.type == TxType.rent_expense:
        stmt = select(Category).where(Category.is_rent == True)
        rent_cat = session.exec(stmt).first()
        if rent_cat:
            rent_cat.current_envelope += txn.amount
            session.add(rent_cat)
        cf.balance += txn.amount

    session.delete(txn)
    session.add(cf)
    session.commit()
    return {"ok": True, "message":"Deleted (basic revert only)."}
