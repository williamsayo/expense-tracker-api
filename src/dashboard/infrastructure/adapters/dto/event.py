from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency


class BaseEventData(BaseModel):
    event_id: str
    occurred_at: datetime
    metadata: dict

class AllocationEventDataModel(BaseModel):
    allocation_id: str
    category: str
    budget_amount: int

class UserCreatedEventData(BaseModel):
    user_id: str
    email: EmailStr


class ExpenseCreatedEventData(BaseModel):
    user_id: str
    name: str | None = None
    merchant: str | None = None
    expense_id: str
    category: Category
    amount: int
    currency: Currency
    date: datetime


class BudgetCreatedEventData(BaseModel):
    name: str | None = None
    user_id: str
    budget_id: str
    currency: Currency
    start_date: date
    end_date: date
    allocations: list[AllocationEventDataModel]


class UserCreatedEventPayload(BaseEventData):
    data: UserCreatedEventData


class ExpenseCreatedEventPayload(BaseEventData):
    data: ExpenseCreatedEventData


class BudgetCreatedEventPayload(BaseEventData):
    data: BudgetCreatedEventData
