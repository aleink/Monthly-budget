# alerts.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from decimal import Decimal

from database import get_session
from models import Alert

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/")
def get_alerts(session: Session = Depends(get_session)):
    """
    List all alerts in the database. 
    (We haven't actually created them yet in the logic, 
     but here's the read endpoint.)
    """
    statement = select(Alert)
    alerts = session.exec(statement).all()
    return alerts
