from decimal import Decimal

from pydantic import Field, BaseModel
from typing import Self, Sequence
from src.dashboard.infrastructure.repositories.schema import (
    ActiveBudgetItem,
    TopExpenseItem,
    TopCategoryItem,
    OverviewItem,
)
from src.shared.infrastructure.adapters.dto.base import BaseReadModel


class ExpenseReadModel(BaseReadModel):
    name: str | None = Field(..., description="The name of the expense.")
    amount: int = Field(..., description="The amount of the expense in cents.")
    currency: str = Field(
        default="EUR", description="The currency of the expense amount."
    )
    category: str = Field(..., description="The category of the expense.")
    merchant: str | None = Field(
        default=None, description="The merchant of the expense."
    )
    date: str = Field(..., description="The date of the expense.")

    @classmethod
    def from_dict(cls, data: TopExpenseItem) -> Self:
        """Creates an ExpenseReadModel instance from a dictionary."""
        return cls(
            name=data["name"],
            amount=data["amount"],
            currency=data.get("currency", "EUR"),
            category=data["category"],
            merchant=data.get("merchant"),
            date=data["date"],
        )


class BudgetReadModel(BaseReadModel):
    name: str | None = Field(default=None, description="The name of the budget.")
    total_amount: int = Field(..., description="The amount of the budget in cents.")
    start_date: str = Field(..., description="The start date of the budget.")
    end_date: str = Field(..., description="The end date of the budget.")

    @classmethod
    def from_dict(cls, data: ActiveBudgetItem | None) -> Self | None:
        """Creates a BudgetReadModel instance from a dictionary."""
        if data is None:
            return None

        return cls(
            name=data.get("name"),
            total_amount=data["total_amount"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )


class TopCategoryReadModel(BaseModel):
    name: str = Field(..., description="The name of the category.")
    amount: int = Field(
        ..., description="The total amount spent in the category in cents."
    )

    @classmethod
    def from_dict(cls, data: TopCategoryItem) -> Self:
        """Creates a TopCategoryReadModel instance from a dictionary."""

        return cls(
            name=data["name"],
            amount=data["amount"],
        )


class DashboardReadModel(BaseModel):
    user_id: str = Field(..., description="The ID of the user.", exclude=True)
    active_budget: BudgetReadModel | None = Field(
        ..., description="The active budget for the user in the period."
    )
    total_spent: int = Field(
        ..., description="The total amount spent by the user in the period."
    )
    total_budgeted: int = Field(
        ..., description="The total amount budgeted for the period."
    )
    top_expense: ExpenseReadModel | None = Field(
        default=None, description="The most expensive expense in the period."
    )
    recent_expenses: list[ExpenseReadModel] = Field(
        ...,
        description="A list of recent expenses by date for the user.",
    )
    top_category: list[TopCategoryReadModel] = Field(
        ...,
        description="A list of top categories by amount spent for the user.",
    )
