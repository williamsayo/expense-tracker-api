from pydantic import BaseModel, Field
from typing import Self, List
from datetime import date, timedelta
from shared.infrastructure.adapters.dto.base import BaseReadModel
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationReadModel,
    BudgetAllocationWriteModel,
    BudgetAllocationUpdateModel,
)


class BudgetModel(BaseModel):
    """Data model for budget."""


class BudgetReadModel(BudgetModel, BaseReadModel):
    """Read model for Budget data."""

    start_date: date = Field(..., description="Date the Budget was made")
    end_date: date = Field(..., description="Date the Budget ends")
    allocations: List[BudgetAllocationReadModel] = Field(
        ..., description="List of budget allocations for the budget"
    )

    @classmethod
    def from_entity(cls, entity: BudgetEntity) -> Self:
        return cls(
            start_date=entity.budget_period.start_date,
            end_date=entity.budget_period.end_date,
            allocations=[
                BudgetAllocationReadModel.from_entity(allocation)
                for allocation in entity.allocations
            ],
        )


class BudgetWriteModel(BudgetModel):
    """Write model for Budget data."""

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
    start_date: date | None = Field(None, description="Date the Budget was made")
    end_date: date | None = Field(None, description="Date the Budget ends")
    allocation: BudgetAllocationUpdateModel | None = Field(
        None, description="Budget allocation for the budget"
    )
