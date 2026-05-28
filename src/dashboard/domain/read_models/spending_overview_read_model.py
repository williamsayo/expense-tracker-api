from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True, frozen=True)
class ExpenseReadModel:
    id: str
    amount: int
    currency: str
    category: str
    date: str
    name: str | None = field(default_factory=lambda: None)
    merchant: str | None = field(default_factory=lambda: None)


@dataclass(slots=True, frozen=True)
class BudgetReadModel:
    id: str
    total_amount: int
    start_date: str
    end_date: str
    name: str | None = field(default_factory=lambda: None)


@dataclass(slots=True, frozen=True)
class CategoryReadModel:
    name: str
    amount: int

@dataclass(slots=True, frozen=True)
class SpendingOverviewReadModel:
    user_id: str
    total_spent: int
    total_budgeted: int
    period: str
    top_expense: ExpenseReadModel | None = field(default_factory=lambda: None)
    active_budget: BudgetReadModel | None = field(default_factory=lambda: None)
    top_categories: list[CategoryReadModel] = field(default_factory=list)
    upcoming_budget: BudgetReadModel | None = field(default_factory=lambda: None)
