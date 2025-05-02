# database.py
from sqlmodel import SQLModel, create_engine, Session
from models import Cashflow

engine = create_engine("sqlite:///budget.db", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # Ensure there's a row for Cashflow
    with Session(engine) as session:
        cf = session.get(Cashflow, 1)
        if not cf:
            cf = Cashflow(balance=0)
            session.add(cf)
            session.commit()

def get_session():
    with Session(engine) as session:
        yield session
