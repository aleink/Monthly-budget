from datetime import datetime, date
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

# ------------------------------------------------
# Category model
# ------------------------------------------------
class CategoryBase(SQLModel):
    name: str
    # We'll store monthly_budget in cents internally
    monthly_budget_cents: int = Field(default=0)


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship to Envelope
    envelopes: List["Envelope"] = Relationship(back_populates="category")

# ------------------------------------------------
# Cycle model
# ------------------------------------------------
class CycleBase(SQLModel):
    # We'll store the total pay in cents for this 2-week period
    pay_amount_cents: int
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
    initial_cents: int = 0
    current_cents: int = 0


class Envelope(EnvelopeBase, table=True):
    cycle_id: Optional[int] = Field(default=None, foreign_key="cycle.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)

    cycle: Optional[Cycle] = Relationship(back_populates="envelopes")
    category: Optional[Category] = Relationship(back_populates="envelopes")

# ------------------------------------------------
# Transaction model
# ------------------------------------------------
class TransactionBase(SQLModel):
    amount_cents: int
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
    # If you want, we could link this to a category or cycle
    # but for now let's keep it simple with just a message.
