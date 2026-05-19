from uuid import UUID
from pydantic import BaseModel, Field
from typing import Annotated
from decimal import Decimal
from src.shared.infrastructure.adapters.dto.base import BaseReadModel
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency

Percentage = Annotated[
    float,
    Field(
        ge=0,
        le=1,
        strict=True,
        description="A percentage value between 0 and 1 inclusive",
    ),
]

class BudgetAllocationModel(BaseModel):
    """Data model for budget allocation."""

    category: Category = Field(..., description="The category of the allocation")

class BudgetAllocationReadModel(BaseReadModel):
    """Read model for BudgetAllocation data."""

    allocation_id: str | UUID = Field(
        ...,
        description="The unique identifier of the budget allocation",
        serialization_alias="id",
    )
    spent_amount: float = Field(
        ...,
        description="The amount spent from this allocation",
        serialization_alias="amountSpent",
    )
    used_percentage: Percentage = Field(..., description="Percentage of budget used")
    category: Category = Field(..., description="The category of the allocation")
    budget_amount: float = Field(
        ..., description="The amount allocated", serialization_alias="allocatedAmount"
    )

class BudgetAllocationWriteModel(BudgetAllocationModel):
    """Write model for BudgetAllocation data."""

    amount: Decimal = Field(
        ...,
        description="The amount allocated",
        ge=Decimal("0.50"),
        decimal_places=2,
        examples=["100.00", "250.50"],
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
