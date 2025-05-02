# schemas.py
from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from models import TxType  # or whatever you called your enum

#
# Category Schemas
#
class CategoryCreate(SQLModel):
    name: str
    is_rent: bool
    biweekly_budget: Decimal
    monthly_budget: Decimal

class CategoryRead(SQLModel):
    id: int
    name: str
    is_rent: bool
    biweekly_budget: Decimal
    monthly_budget: Decimal
    current_envelope: Decimal

    class Config:
        # For Pydantic v2 + SQLModel, replace "orm_mode = True" with:
        from_attributes = True

#
# Transaction Schemas
#
class TransactionCreate(SQLModel):
    type: TxType
    amount: Decimal
    # Make this optional so paychecks/ATM deposits don't require a category
    category_id: Optional[int] = Field(default=None)

class TransactionRead(SQLModel):
    id: int
    amount: Decimal
    timestamp: datetime
    type: TxType
    category_id: Optional[int]

    class Config:
        from_attributes = True

#
# If you have a Cashflow or Budget read schema, you can define it similarly
# with from_attributes = True if it's returning DB objects.
#
