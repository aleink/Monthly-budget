from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Transaction, Envelope, Cycle
from schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionRead)
def create_transaction(data: TransactionCreate, session: Session = Depends(get_session)):
    cycle = session.get(Cycle, data.cycle_id)
    if not cycle:
        raise HTTPException(status_code=400, detail="Cycle not found.")

    stmt_env = select(Envelope).where(
        (Envelope.cycle_id == data.cycle_id)
        & (Envelope.category_id == data.category_id)
    )
    envelope = session.exec(stmt_env).first()
    if not envelope:
        raise HTTPException(status_code=400, detail="Envelope not found.")

    envelope.current = envelope.current - data.amount

    txn = Transaction(
        cycle_id=data.cycle_id,
        category_id=data.category_id,
        amount=data.amount
    )
    session.add(txn)
    session.add(envelope)
    session.commit()
    session.refresh(txn)
    return txn

@router.get("/", response_model=list[TransactionRead])
def get_transactions(session: Session = Depends(get_session)):
    stmt = select(Transaction)
    return session.exec(stmt).all()

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    txn = session.get(Transaction, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # refund
    stmt_env = select(Envelope).where(
        (Envelope.cycle_id == txn.cycle_id)
        & (Envelope.category_id == txn.category_id)
    )
    envelope = session.exec(stmt_env).first()
    if envelope:
        envelope.current += txn.amount

    session.delete(txn)
    session.commit()
    return {"ok": True, "message": "Transaction deleted (and envelope refunded)."}
