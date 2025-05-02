# database.py
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# Create a local SQLite URL at 'budget.db'
sqlite_file_name = "budget.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    from models import Category, Cycle, Envelope, Transaction, Alert
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
