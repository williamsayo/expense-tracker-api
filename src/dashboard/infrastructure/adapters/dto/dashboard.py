from decimal import Decimal

from pydantic import Field, BaseModel
from typing import Self
from src.dashboard.infrastructure.repositories.schema import BudgetSchema, ExpenseSchema
from src.shared.infrastructure.adapters.dto.base import BaseReadModel


class ExpenseReadModel(BaseReadModel):
    name: str = Field(..., description="The name of the expense.")
    amount: float = Field(..., description="The amount of the expense in dollars.")
    currency: str = Field(
        default="EUR", description="The currency of the expense amount."
    )
    category: str = Field(..., description="The category of the expense.")
    merchant: str | None = Field(
        default=None, description="The merchant of the expense."
    )
    date: str = Field(..., description="The date of the expense.")

    @classmethod
    def from_dict(cls, data: ExpenseSchema | dict) -> Self:
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
    total_amount: float = Field(..., description="The amount of the budget.")
    start_date: str = Field(..., description="The start date of the budget.")
    end_date: str = Field(..., description="The end date of the budget.")

    @classmethod
    def from_dict(cls, data: BudgetSchema | dict | None) -> Self | None:
        """Creates a BudgetReadModel instance from a dictionary."""
        if data is None:
            return None

        return cls(
            name=data.get("name"),
            total_amount=data["total_amount"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )


class DashboardReadModel(BaseReadModel):
    active_budget: BudgetReadModel | None = Field(
        default=None, description="The active budget for the user in the period."
    )
    total_spent: float = Field(
        default=0.0, description="The total amount spent by the user in the period."
    )
    total_budgeted: float = Field(
        default=0.0, description="The total amount budgeted for the period."
    )
    top_expense: ExpenseReadModel | None = Field(
        default=None, description="The most expensive expense in the period."
    )
    recent_expenses: list[ExpenseReadModel] = Field(
        default_factory=list,
        description="A list of recent expenses by date for the user.",
    )


class DashboardWriteModel(BaseModel):
    active_budget: BudgetReadModel | None = Field(
        ..., description="The active budget for the user in the period."
    )
    total_spent: Decimal = Field(
        ..., description="The total amount spent by the user in the period."
    )
    total_budgeted: Decimal = Field(
        ..., description="The total amount budgeted for the period."
    )
    top_expense: ExpenseReadModel | None = Field(
        ..., description="The most expensive expense in the period."
    )
    top_category: dict[str, str] = Field(
        ...,
        description="A dictionary mapping expense categories to total amounts spent in those categories.",
    )
    recent_expenses: list[ExpenseReadModel] = Field(
        ...,
        description="A list of recent expenses by date for the user.",
    )
