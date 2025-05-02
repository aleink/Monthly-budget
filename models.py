from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DECIMAL

# --- Category DB Model ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    monthly_budget: Decimal = Field(sa_column=Column(DECIMAL(10, 2)))

    envelopes: List["Envelope"] = Relationship(back_populates="category")

# --- Cycle DB Model ---
class Cycle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pay_amount: Decimal = Field(sa_column=Column(DECIMAL(10, 2)), default=Decimal("0.00"))
    start_date: date  # "table=True" means this is stored as a real DATE

    envelopes: List["Envelope"] = Relationship(back_populates="cycle")
    transactions: List["Transaction"] = Relationship(back_populates="cycle")

# --- Envelope DB Model ---
class Envelope(SQLModel, table=True):
    cycle_id: Optional[int] = Field(default=None, foreign_key="cycle.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)
    initial: Decimal = Field(sa_column=Column(DECIMAL(10, 2)), default=Decimal("0.00"))
    current: Decimal = Field(sa_column=Column(DECIMAL(10, 2)), default=Decimal("0.00"))

    cycle: Optional[Cycle] = Relationship(back_populates="envelopes")
    category: Optional[Category] = Relationship(back_populates="envelopes")

# --- Transaction DB Model ---
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cycle_id: int = Field(foreign_key="cycle.id")
    category_id: int = Field(foreign_key="category.id")
    amount: Decimal = Field(sa_column=Column(DECIMAL(10, 2)), default=Decimal("0.00"))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    cycle: Optional[Cycle] = Relationship(back_populates="transactions")

# --- Alert DB Model ---
class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
