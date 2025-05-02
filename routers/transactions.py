# transactions.py
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Transaction, Envelope, Cycle

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=Transaction)
def create_transaction(txn: Transaction, session: Session = Depends(get_session)):
    """
    Record an expense. We deduct txn.amount from the corresponding envelope's current.
    """
    # 1) Validate the cycle/category exist:
    cycle = session.get(Cycle, txn.cycle_id)
    if not cycle:
        raise HTTPException(status_code=400, detail="Cycle not found.")
    
    # We should also ensure the category is valid, but the foreign key ensures that.

    # 2) Deduct from the envelope
    stmt_env = select(Envelope).where(
        (Envelope.cycle_id == txn.cycle_id) &
        (Envelope.category_id == txn.category_id)
    )
    envelope = session.exec(stmt_env).first()
    if not envelope:
        raise HTTPException(status_code=400, detail="Envelope not found.")

    envelope.current = envelope.current - txn.amount
    
    session.add(txn)
    session.add(envelope)
    session.commit()
    session.refresh(txn)

    return txn

@router.get("/", response_model=list[Transaction])
def get_transactions(session: Session = Depends(get_session)):
    """
    List all transactions.
    """
    statement = select(Transaction)
    txns = session.exec(statement).all()
    return txns

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    """
    Delete a transaction by ID, and refund its amount to the envelope.
    """
    txn = session.get(Transaction, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Refund the envelope
    stmt_env = select(Envelope).where(
        (Envelope.cycle_id == txn.cycle_id) &
        (Envelope.category_id == txn.category_id)
    )
    envelope = session.exec(stmt_env).first()
    if envelope:
        envelope.current = envelope.current + txn.amount
        session.add(envelope)

    session.delete(txn)
    session.commit()
    return {"ok": True, "message": "Transaction deleted (and envelope refunded)."}
