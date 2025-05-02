# models.py
from typing import Optional
from decimal import Decimal
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DECIMAL, Boolean
import enum

class TxType(str, enum.Enum):
    paycheck = "paycheck"
    atm = "atm"
    expense = "expense"
    rent_expense = "rent_expense"

class Cashflow(SQLModel, table=True):
    """
    Holds the available cash that's not allocated to any envelope.
    """
    id: Optional[int] = Field(default=1, primary_key=True)
    balance: Decimal = Field(sa_column=Column(DECIMAL(10,2)), default=Decimal("0.00"))

class Category(SQLModel, table=True):
    """
    For non-rent categories, 'biweekly_budget' is how much each paycheck
    sets aside. For rent, we store 'monthly_budget' and is_rent=True.
    'current_envelope' is how much is currently allocated to that category.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    is_rent: bool = Field(default=False, sa_column=Column(Boolean))

    # For non-rent, this is used. For rent, we use monthly_budget below.
    biweekly_budget: Decimal = Field(sa_column=Column(DECIMAL(10,2)), default=Decimal("0.00"))

    # For rent, this is used. For non-rent, it can remain 0.
    monthly_budget: Decimal = Field(sa_column=Column(DECIMAL(10,2)), default=Decimal("0.00"))

    # This is how much money is allocated right now (envelope).
    current_envelope: Decimal = Field(sa_column=Column(DECIMAL(10,2)), default=Decimal("0.00"))

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: Decimal = Field(sa_column=Column(DECIMAL(10,2)), default=Decimal("0.00"))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: TxType

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
