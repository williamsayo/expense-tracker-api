from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Self
from datetime import datetime, UTC
from decimal import Decimal
from shared.infrastructure.adapters.dto.base import BaseReadModel
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from expenses.domain.entities.expense_entity import ExpenseEntity


class ExpenseModel(BaseModel):
    """Data model for expense."""

    name: str | None = Field(None, description="Name of the expense")
    category: CategoryType
    note: str | None = Field(None, description="Note about the expense")


class ExpenseReadModel(ExpenseModel, BaseReadModel):
    """Read model for expense data."""

    id: str | UUID
    amount: float = Field(..., description="Amount of the expense in cents")
    currency: Currency = Field(..., description="Currency of the expense")
    date: datetime = Field(..., description="Date the expense was made")

    @classmethod
    def from_entity(cls, entity: ExpenseEntity) -> Self:
        return cls(
            id=entity.id.value,
            category=entity.category.name,
            amount=entity.money.to_currency(),
            note=entity.note,
            date=entity.date,
            currency=entity.money.currency,
            name=entity.name,
        )


class ExpenseOverviewReadModel(BaseReadModel):
    """Read model for expense data."""

    total_spent: float
    highest_expense: ExpenseReadModel | None
    recent_expenses: List[ExpenseReadModel]

class ExpenseWriteModel(ExpenseModel):
    """Write model for expense data."""

    date: datetime = Field(
        default=datetime.now(UTC), description="Date the expense was made"
    )
    currency: Currency = Field(default=Currency.EUR)
    amount: Decimal = Field(
        ...,
        decimal_places=2,
        ge=Decimal("0.1"),
        description="amount of the expense in the specified currency",
        examples=[100.00],
    )


class ExpenseUpdateModel(ExpenseModel):
    """Update model for expense data."""

    date: datetime | None = Field(None, description="Date the expense was made")
    category: CategoryType | None = None
    amount: Decimal | None = Field(None, decimal_places=2, ge=Decimal("0.1"))
    currency: Currency | None = Field(default=None)
