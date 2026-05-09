from typing import Never, NotRequired, TypedDict, Self
from boilerplate import Entity, UniqueEntityId
from result import Either, result_ok
from src.shared.domain.types.currency_types import Currency
from src.spending.budgeting.domain.value_objects.amount_value_object import (
    AmountValueObject,
)
from src.shared.domain.value_objects.category_value_object import CategoryValueObject


class BudgetAllocationEntityProps(TypedDict):
    """Typed dictionary for budget allocation entity fields."""

    amount: AmountValueObject
    category: CategoryValueObject
    spent_amount: NotRequired[float]


class BudgetAllocationEntity(Entity[BudgetAllocationEntityProps]):
    """Entity for budget allocation."""

    def __init__(
        self,
        props: BudgetAllocationEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ):
        super().__init__(props, id, version)

    @property
    def amount(self) -> AmountValueObject:
        return self.props["amount"]

    @property
    def category(self) -> CategoryValueObject:
        return self.props["category"]

    def apply_spending(self, amount: float) -> None:
        amount_spent = self.props.get("spent_amount", 0)
        self.props["spent_amount"] = amount_spent + amount

    @classmethod
    def create(
        cls,
        props: BudgetAllocationEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))

    @classmethod
    def existing_budget_allocation(
        cls, props: BudgetAllocationEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))
