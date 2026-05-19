from pydantic import BaseModel, Field
from uuid import UUID
from typing import Annotated, Self, List
from datetime import date, timedelta
from src.shared.infrastructure.adapters.dto.base import BaseReadModel
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationReadModel,
    BudgetAllocationWriteModel,
    BudgetAllocationUpdateModel,
)
from src.shared.domain.types.currency_types import Currency
from src.spending.expenses.infrastructure.adapters.dto.expense import ExpenseReadModel

Percentage = Annotated[
    float,
    Field(
        ge=0,
        le=1,
        strict=True,
        description="A percentage value between 0 and 1 inclusive",
    ),
]


class BudgetModel(BaseModel):
    """Data model for budget."""

    name: str | None = Field(None, description="Name of the budget")


class BudgetReadModel(BudgetModel, BaseReadModel):
    """Read model for Budget data."""

    user_id: UUID = Field(
        ..., description="The unique identifier of the user", exclude=True
    )
    budget_id: str | UUID = Field(
        ...,
        description="The unique identifier of the budget",
        serialization_alias="id",
    )
    name: str | None = Field(..., description="Name of the budget")
    currency: Currency = Field(..., description="Currency code (e.g., 'USD', 'EUR')")
    total_amount: float = Field(..., description="Total budget amount")
    amount_spent: float = Field(..., description="Total amount spent")
    remaining_amount: float = Field(..., description="Remaining budget amount")
    used_percentage: Percentage = Field(..., description="Percentage of budget used")
    remaining_percentage: Percentage = Field(
        default=100, description="Remaining budget percentage"
    )
    start_date: date = Field(..., description="Date the Budget was made")
    end_date: date = Field(..., description="Date the Budget ends")
    allocations: List[BudgetAllocationReadModel] = Field(
        ..., description="List of budget allocations for the budget"
    )
    expenses: List[ExpenseReadModel] = Field(
        ..., description="List of expenses associated with the budget"
    )

    @classmethod
    def from_entity(cls, entity: BudgetEntity) -> Self:
        return cls(
            budget_id=entity.id.value,
            name=entity.name,
            currency=entity.currency,
            start_date=entity.budget_period.start_date,
            end_date=entity.budget_period.end_date,
            allocations=[
                BudgetAllocationReadModel.from_entity(allocation)
                for allocation in entity.allocations
            ],
            user_id=entity.user_id,
            expenses=[],
            total_amount=0,
            amount_spent=0,
            remaining_amount=0,
            used_percentage=0,
            remaining_percentage=0,
        )


class BudgetOverviewReadModel(BaseReadModel):
    """Read model for Budget data."""

    total_allocated: float = Field(..., description="Total budget amount")
    active_budget: BudgetReadModel | None = Field(
        ..., description="Active budget for the user"
    )
    recent_budgets: List[BudgetReadModel] = Field(
        ..., description="List of recent budgets for the user"
    )
    upcoming_budget: BudgetReadModel | None = Field(
        ..., description="upcoming budgets for the user"
    )


class BudgetWriteModel(BudgetModel):
    """Write model for Budget data."""

    currency: Currency = Field(
        default=Currency.EUR, description="Currency code (e.g., 'USD', 'EUR')"
    )
    start_date: date = Field(
        default=date.today(), description="Date the Budget was made"
    )
    end_date: date = Field(
        default=date.today() + timedelta(days=30), description="Date the Budget ends"
    )
    allocations: List[BudgetAllocationWriteModel] = Field(
        ..., description="List of budget allocations for the budget"
    )


class BudgetUpdateModel(BudgetModel):
    """Update model for Budget data."""

    currency: Currency | None = Field(
        default=Currency.EUR, description="Currency code (e.g., 'USD', 'EUR')"
    )
    start_date: date | None = Field(None, description="Date the Budget was made")
    end_date: date | None = Field(None, description="Date the Budget ends")
    allocation: BudgetAllocationUpdateModel | None = Field(
        None, description="Budget allocation for the budget"
    )
