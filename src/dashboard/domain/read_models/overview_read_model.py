from decimal import Decimal
from typing import TypedDict, List
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BudgetReadModel:
    name: str | None
    total_amount: int
    spent_amount: int
    start_date: str
    end_date: str


@dataclass(slots=True, frozen=True)
class ExpenseReadModel:
    name: str | None
    amount: int
    currency: str
    category: str
    merchant: str | None
    date: str


class DashboardOverviewReadModelProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    top_expense: ExpenseReadModel | None
    recent_expenses: List[ExpenseReadModel]
    total_spent: int
    total_budgeted: int
    active_budget: BudgetReadModel | None


class TopCategoryReadModel(TypedDict):
    name: str
    amount: int

@dataclass(slots=True, frozen=True)
class DashboardOverviewReadModel:
    """Read model for expense overview."""

    user_id: str
    top_expense: ExpenseReadModel | None
    recent_expenses: List[ExpenseReadModel]
    total_spent: int
    active_budget: BudgetReadModel | None
    total_budgeted: int
    top_category: list[TopCategoryReadModel]
