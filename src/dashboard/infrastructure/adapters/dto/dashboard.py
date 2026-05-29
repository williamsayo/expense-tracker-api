from datetime import date
from pydantic import Field, BaseModel, field_serializer
from typing import Self
from src.dashboard.infrastructure.repositories.schema import CategoryItem
from src.shared.infrastructure.adapters.dto.base import BaseReadModel


class CategoryReadModel(BaseModel):
    name: str = Field(
        ..., description="The name of the category.", examples=["Food", "Transport"]
    )
    amount: int = Field(
        ..., description="The total amount spent in the category in cents."
    )

    @classmethod
    def from_dict(cls, data: CategoryItem) -> Self:
        """Creates a CategoryReadModel instance from a dictionary."""

        return cls(
            name=data["name"],
            amount=data["amount"],
        )

    @field_serializer("amount")
    def serialize_amount(self, value: int) -> float:
        return value / 100


class SpendingInsightReadModel(BaseReadModel):
    period: str = Field(
        ...,
        description="The month of the spending insight in the format 'Year-Month'.",
        examples=["2024-06"],
    )
    total_spent: int = Field(..., description="The total amount spent in the period.")
    total_budgeted: int = Field(
        ..., description="The total amount budgeted for the period."
    )

    @field_serializer("total_spent")
    def serialize_total_spent(self, value: int) -> float:
        return value / 100

    @field_serializer("total_budgeted")
    def serialize_total_budgeted(self, value: int) -> float:
        return value / 100


# Public model for API responses, excluding user_id and other internal fields
class BudgetPublicModel(BaseReadModel):
    id: str = Field(
        ...,
        description="The ID of the budget.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    name: str | None = Field(
        default=None, description="The name of the budget.", examples=["June Budget"]
    )
    total_amount: int = Field(..., description="The amount of the budget in cents.")
    start_date: str = Field(
        ..., description="The start date of the budget.", examples=["2024-06-01"]
    )
    end_date: str = Field(
        ..., description="The end date of the budget.", examples=["2024-06-30"]
    )

    @field_serializer("total_amount")
    def serialize_total_amount(self, value: int) -> float:
        return value / 100


class ExpensePublicModel(BaseReadModel):
    id: str = Field(
        ...,
        description="The ID of the expense.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    name: str | None = Field(
        ..., description="The name of the expense.", examples=["Dinner at restaurant"]
    )
    merchant: str | None = Field(
        ...,
        description="The merchant of the expense.",
        examples=["Amazon", "Starbucks"],
    )
    amount: int = Field(..., description="The amount of the expense in cents.")
    currency: str = Field(
        default="EUR",
        description="The currency of the expense amount.",
        examples=["EUR"],
    )
    category: str = Field(
        ..., description="The category of the expense.", examples=["Food", "Transport"]
    )
    date: str = Field(
        ..., description="The date of the expense.", examples=["2024-06-15"]
    )

    @field_serializer("amount")
    def serialize_amount(self, value: int) -> float:
        return value / 100


class DashboardPublicModel(BaseReadModel):
    total_spent: int = Field(
        ..., description="The total amount spent by the user in the period."
    )
    total_budgeted: int = Field(
        ..., description="The total amount budgeted for the period."
    )
    top_expense: ExpensePublicModel | None = Field(
        default=None, description="The most expensive expense in the period."
    )
    active_budget: BudgetPublicModel | None = Field(
        default=None, description="The active budget for the user in the period."
    )
    top_categories: list[CategoryReadModel] = Field(
        default_factory=list,
        description="A list of top categories by amount spent for the user.",
    )
    recent_expenses: list[ExpensePublicModel] = Field(
        default_factory=list,
        description="A list of recent expenses by date for the user.",
    )
    recent_budgets: list[BudgetPublicModel] = Field(
        default_factory=list, description="List of recent budgets for the user"
    )
    upcoming_budget: BudgetPublicModel | None = Field(
        default=None, description="upcoming budgets for the user"
    )
    spending_insights: list[SpendingInsightReadModel] = Field(
        default_factory=list,
        description="A list of spending insights for the user in the period.",
    )

    @field_serializer("total_spent")
    def serialize_total_spent(self, value: int) -> float:
        return value / 100

    @field_serializer("total_budgeted")
    def serialize_total_budgeted(self, value: int) -> float:
        return value / 100
