from typing import Never, TypedDict, Self
from boilerplate import Entity, UniqueEntityId
from result import Either, result_ok
from budgeting.domain.value_objects.amount_value_object import AmountValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject


class BudgetAllocationEntityProps(TypedDict):
    """Typed dictionary for budget allocation entity fields."""

    amount: AmountValueObject
    category: CategoryValueObject


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
