from typing import TypedDict, List
from uuid import UUID
from budgeting.domain.read_models.budget_summary import (
    BudgetSummaryReadModel,
)


class BudgetOverviewReadModelProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    user_id: UUID
    recent_budgets: List[BudgetSummaryReadModel]
    upcoming_budget: BudgetSummaryReadModel | None
    active_budget: BudgetSummaryReadModel | None
    total_allocated: float


class BudgetOverviewReadModel:
    """Read model for budget overview."""

    def __init__(
        self,
        props: BudgetOverviewReadModelProps,
    ):
        self._user_id = props["user_id"]
        self._recent_budgets = props["recent_budgets"]
        self._upcoming_budget = props["upcoming_budget"]
        self._active_budget = props["active_budget"]
        self._total_allocated = props["total_allocated"]

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def recent_budgets(self) -> List[BudgetSummaryReadModel]:
        return self._recent_budgets

    @property
    def upcoming_budget(self) -> BudgetSummaryReadModel | None:
        return self._upcoming_budget

    @property
    def total_allocated(self) -> float:
        return self._total_allocated

    @property
    def active_budget(self) -> BudgetSummaryReadModel | None:
        return self._active_budget