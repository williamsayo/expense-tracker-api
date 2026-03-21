from typing import Never, TypedDict, Self
from boilerplate.domain.entity import Entity
from boilerplate.domain.unique_entity_id import UniqueEntityId
from result import Either, result_ok
from shared.domain.value_objects.money_value_object import MoneyValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject


class BudgetAllocationEntityProps(TypedDict):
    """Typed dictionary for budget allocation entity fields."""

    money: MoneyValueObject
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
    def money(self) -> MoneyValueObject:
        return self.props["money"]

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
