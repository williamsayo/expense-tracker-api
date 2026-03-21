from pydantic import BaseModel, Field
from typing import Self
from decimal import Decimal
from shared.infrastructure.adapters.dto.base import BaseReadModel
from budgeting.domain.entities.budget_allocation_entity import BudgetAllocationEntity
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency


class BudgetAllocationModel(BaseModel):
    """Data model for budget allocation."""

    amount: Decimal = Field(
        ..., description="The amount allocated", ge=Decimal("0.50"), decimal_places=2
    )
    category: CategoryType = Field(..., description="The category of the allocation")


class BudgetAllocationReadModel(BudgetAllocationModel, BaseReadModel):
    """Read model for BudgetAllocation data."""

    amount: str = Field(
        ...,
        description="The amount allocated as a formatted currency string to preserve precision",
    )

    @classmethod
    def from_entity(cls, entity: BudgetAllocationEntity) -> Self:
        return cls(
            amount=entity.money.to_currency(),
            category=entity.category.name,
        )


class BudgetAllocationWriteModel(BudgetAllocationModel):
    """Write model for BudgetAllocation data."""

    currency: Currency = Field(
        default=Currency.EUR, description="The currency of the allocation"
    )


class BudgetAllocationUpdateModel(BudgetAllocationModel):
    """Update model for BudgetAllocation data."""

    id: str = Field(..., description="The unique identifier of the budget allocation")
    amount: Decimal | None = Field(
        None,
        description="The amount allocated",
        ge=Decimal("0.50"),
        decimal_places=2,
        max_digits=12,
        examples=["100.00", "250.50"],
    )
    currency: Currency | None = Field(
        None, description="The currency of the allocation"
    )
