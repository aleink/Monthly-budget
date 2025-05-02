# schemas.py
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field

#
# Category Schemas
#
class CategoryCreate(SQLModel):
    name: str
    monthly_budget: Decimal

class CategoryRead(SQLModel):
    id: int
    name: str
    monthly_budget: Decimal

    class Config:
        # This tells Pydantic/SQLModel it's OK
        # to read data from ORM objects
        orm_mode = True

#
# Cycle Schemas
#
class CycleCreate(SQLModel):
    pay_amount: Decimal
    start_date: date

class CycleRead(SQLModel):
    id: int
    pay_amount: Decimal
    start_date: date

    class Config:
        orm_mode = True

#
# Transaction Schemas
#
class TransactionCreate(SQLModel):
    cycle_id: int
    category_id: int
    amount: Decimal

class TransactionRead(SQLModel):
    id: int
    cycle_id: int
    category_id: int
    amount: Decimal
    timestamp: datetime

    class Config:
        orm_mode = True
