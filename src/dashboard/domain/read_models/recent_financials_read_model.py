from dataclasses import dataclass, field
from .spending_overview_read_model import ExpenseReadModel, BudgetReadModel


@dataclass(slots=True, frozen=True)
class RecentFinancialsReadModel:
    user_id: str
    recent_expenses: list[ExpenseReadModel] = field(default_factory=list)
    recent_budgets: list[BudgetReadModel] = field(default_factory=list)
  