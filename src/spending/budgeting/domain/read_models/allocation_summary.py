from typing import TypedDict
from uuid import UUID
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency


class BudgetAllocationSummaryReadModelProps(TypedDict):
    """Typed dictionary for budget allocation summary entity fields."""

    allocation_id: UUID
    budget_amount: float
    category: Category
    spent_amount: float


class BudgetAllocationSummaryReadModel:
    """Entity for budget allocation summary."""

    def __init__(
        self,
        props: BudgetAllocationSummaryReadModelProps,
    ):
        self._allocation_id = props["allocation_id"]
        self._budget_amount = props["budget_amount"]
        self._category = props["category"]
        self._spent_amount = props["spent_amount"]

    @property
    def allocation_id(self) -> UUID:
        return self._allocation_id

    @property
    def budget_amount(self) -> float:
        return self._budget_amount / 100

    @property
    def category(self) -> Category:
        return self._category

    @property
    def spent_amount(self) -> float:
        return self._spent_amount / 100

    @property
    def remaining_amount(self) -> float:
        return max(self.budget_amount - self.spent_amount, 0)

    @property
    def used_percentage(self) -> float:
        if self.budget_amount <= 0:
            return 0.0
        return min(self.spent_amount / self.budget_amount, 1.0)

    @property
    def left_percentage(self) -> float:
        return max(1.0 - self.used_percentage, 0.0)

    def apply_spending(self, amount: int, currency: Currency) -> None:
        self._spent_amount = self.spent_amount + amount
