from typing import Any, Dict, TypedDict


class InsightOverviewSchema(TypedDict):
    period: str
    content: Dict[Any, Any]
    status: str


class ExpenseSchema(TypedDict):
    name: str
    amount: float
    currency: str
    category: str
    merchant: str | None
    date: str


class BudgetSchema(TypedDict):
    name: str | None
    total_amount: float
    spent_amount: float
    start_date: str
    end_date: str


class RecentExpensesSchema(TypedDict):
    expenses: list[ExpenseSchema]


class SpendingSummarySchema(TypedDict):
    """Schema for the dashboard module."""

    total_spent: float
    total_budgeted: float
    remaining_budget: float
    top_category: dict
    top_expense: ExpenseSchema | None
    active_budget: BudgetSchema | None
