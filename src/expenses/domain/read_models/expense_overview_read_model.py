from typing import TypedDict, List
from uuid import UUID
from expenses.domain.read_models.expense_read_model import ExpenseReadModel


class ExpenseOverviewReadModelProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    user_id: UUID
    recent_expenses: List[ExpenseReadModel]
    total_spent: float
    highest_expense: ExpenseReadModel | None

class ExpenseOverviewReadModel:
    """Read model for expense overview."""

    def __init__(
        self,
        props: ExpenseOverviewReadModelProps,
    ):
        self._user_id = props["user_id"]
        self._recent_expenses = props["recent_expenses"]
        self._total_spent = props["total_spent"]
        self._highest_expense = props["highest_expense"]

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def recent_expenses(self) -> List[ExpenseReadModel]:
        return self._recent_expenses

    @property
    def total_spent(self) -> float:
        return self._total_spent / 100  # Convert cents to dollars

    @property
    def highest_expense(self) -> ExpenseReadModel | None:
        return self._highest_expense
