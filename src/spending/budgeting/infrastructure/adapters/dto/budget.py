from pydantic import BaseModel, Field, computed_field
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
from functools import cached_property

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


class BudgetSummaryReadModel(BudgetModel, BaseReadModel):
    """Read model for budget summary data."""

    name: str | None = Field(..., description="Name of the budget")
    currency: Currency = Field(..., description="Currency code (e.g., 'USD', 'EUR')")
    start_date: date = Field(..., description="Date the Budget was made")
    end_date: date = Field(..., description="Date the Budget ends")


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
    start_date: date = Field(..., description="Date the Budget was made")
    end_date: date = Field(..., description="Date the Budget ends")
    allocations: List[BudgetAllocationReadModel] = Field(
        ..., description="List of budget allocations for the budget"
    )
    expenses: List[ExpenseReadModel] = Field(
        ..., description="List of expenses associated with the budget"
    )

    @cached_property
    def total_budgeted(self) -> int:
        """Calculates the total budgeted amount for the budget."""
        return sum(allocation.budget_amount for allocation in self.allocations)

    @cached_property
    def total_spent(self) -> int:
        """Calculates the total spent amount for the budget."""
        return sum(allocation.spent_amount for allocation in self.allocations)

    @cached_property
    def percentage_used(self) -> float:
        """Calculates the percentage of the budget that has been used."""
        if self.total_budgeted <= 0:
            return 0.0
        return min(self.total_spent / self.total_budgeted, 1.0)

    @computed_field(description="Total budget amount")
    @property
    def total_amount(self) -> float:
        return self.total_budgeted / 100

    @computed_field(description="Total amount spent")
    @property
    def amount_spent(self) -> float:
        return self.total_spent / 100

    @computed_field(description="Remaining amount in the budget")
    @property
    def remaining_amount(self) -> float:
        return max(self.total_budgeted - self.total_spent, 0) / 100

    @computed_field(description="Percentage of budget used")
    @property
    def used_percentage(self) -> float:
        return self.percentage_used

    @computed_field(description="Remaining percentage of the budget")
    @property
    def remaining_percentage(self) -> float:
        return max(1.0 - self.percentage_used, 0.0)

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
