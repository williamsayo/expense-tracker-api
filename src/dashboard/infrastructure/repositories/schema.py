from typing import Any, Dict, TypedDict


class InsightOverviewItem(TypedDict):
    period: str
    content: Dict[Any, Any]
    status: str


class ExpenseProjectionItem(TypedDict):
    id: str
    amount: int
    currency: str
    category: str
    date: str


class BudgetProjectionItem(TypedDict):
    id: str
    total_amount: int
    spent_amount: int
    start_date: str
    end_date: str


class CategoryItem(TypedDict):
    name: str
    amount: int


# Schema for the dashboard module
class ExpenseItem(TypedDict):
    id: str
    name: str | None
    merchant: str | None
    amount: int
    currency: str
    category: str
    date: str


class ActiveBudgetItem(TypedDict):
    id: str
    name: str | None
    total_amount: int
    start_date: str
    end_date: str


class OverviewItem(TypedDict):
    """Schema for the dashboard module."""

    user_id: str
    total_spent: int
    total_budgeted: int
    top_category: list[CategoryItem]
    top_expense: ExpenseItem | None
    active_budget: ActiveBudgetItem | None
    recent_expenses: list[ExpenseItem]
