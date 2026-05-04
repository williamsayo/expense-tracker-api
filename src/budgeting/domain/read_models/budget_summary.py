from typing import TypedDict, List
from datetime import date
from uuid import UUID
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from budgeting.domain.read_models.allocation_summary import (
    BudgetAllocationSummaryReadModel,
)


class BudgetSummaryReadModelProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    budget_id: UUID
    name: str | None
    user_id: UUID
    allocations: List[BudgetAllocationSummaryReadModel]
    start_date: date
    end_date: date
    currency: Currency


class BudgetSummaryReadModel:
    """Read model for budget."""

    def __init__(
        self,
        props: BudgetSummaryReadModelProps,
    ):
        self._budget_id = props["budget_id"]
        self._user_id = props["user_id"]
        self._allocations = props["allocations"]
        self._start_date = props["start_date"]
        self._end_date = props["end_date"]
        self._currency = props["currency"]
        self._name = props["name"]

    @property
    def budget_id(self) -> UUID:
        return self._budget_id
    
    @property
    def name(self) -> str | None:
        return self._name

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def allocations(self) -> List[BudgetAllocationSummaryReadModel]:
        return self._allocations

    @property
    def start_date(self) -> date:
        return self._start_date

    @property
    def end_date(self) -> date:
        return self._end_date

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def total_amount(self) -> float:
        return sum(allocation.budget_amount for allocation in self.allocations)

    @property
    def amount_spent(self) -> float:
        return sum(allocation.spent_amount for allocation in self.allocations)

    @property
    def remaining_amount(self) -> float:
        return max(self.total_amount - self.amount_spent, 0)

    @property
    def used_percentage(self) -> float:
        if self.total_amount <= 0:
            return 0.0
        return min(self.amount_spent / self.total_amount, 1.0)

    @property
    def remaining_percentage(self) -> float:
        return max(1.0 - self.used_percentage, 0.0)

    def track_expense(
        self, *, category: CategoryType, amount: int, currency: Currency
    ) -> None:

        for allocation in self.allocations:
            if allocation.category == category:
                allocation.apply_spending(amount, currency)
