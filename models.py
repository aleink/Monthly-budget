from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DECIMAL

# ------------------------------------------------
# Category model
# ------------------------------------------------
class CategoryBase(SQLModel):
    name: str

    # We'll store monthly budget in decimal dollars, e.g. 200.00
    monthly_budget: Decimal = Field(
        default=Decimal("0.00"),
        sa_column=Column(DECIMAL(10, 2))
    )


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship to Envelope
    envelopes: List["Envelope"] = Relationship(back_populates="category")

# ------------------------------------------------
# Cycle model
# ------------------------------------------------
class CycleBase(SQLModel):
    # total pay for this 2-week period as decimal dollars, e.g. 1000.00
    pay_amount: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2)),
        default=Decimal("0.00")
    )
    start_date: date  # The date this cycle starts


class Cycle(CycleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship to Envelope and Transactions
    envelopes: List["Envelope"] = Relationship(back_populates="cycle")
    transactions: List["Transaction"] = Relationship(back_populates="cycle")

# ------------------------------------------------
# Envelope model
# ------------------------------------------------
class EnvelopeBase(SQLModel):
    # initial_dollars set when the cycle is created
    initial: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2)),
        default=Decimal("0.00")
    )
    # current_dollars will decrease when we log transactions
    current: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2)),
        default=Decimal("0.00")
    )


class Envelope(EnvelopeBase, table=True):
    cycle_id: Optional[int] = Field(default=None, foreign_key="cycle.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)

    cycle: Optional[Cycle] = Relationship(back_populates="envelopes")
    category: Optional[Category] = Relationship(back_populates="envelopes")

# ------------------------------------------------
# Transaction model
# ------------------------------------------------
class TransactionBase(SQLModel):
    # how much was spent in this transaction, e.g. 15.99
    amount: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2)),
        default=Decimal("0.00")
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Transaction(TransactionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cycle_id: int = Field(foreign_key="cycle.id")
    category_id: int = Field(foreign_key="category.id")

    cycle: Optional[Cycle] = Relationship(back_populates="transactions")

# ------------------------------------------------
# Alert model (optional)
# ------------------------------------------------
class AlertBase(SQLModel):
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Alert(AlertBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # For advanced usage, you might link to a category_id or cycle_id
    # but for now we'll just store a free-form message.
