from decimal import Decimal
from typing import Never, TypedDict, Self
from datetime import date
from boilerplate.errors.domain import DomainRuleError
from boilerplate.domain.aggregate_root import AggregateRoot
from boilerplate.domain.unique_entity_id import UniqueEntityId
from result import Either, is_fail, result_fail, result_ok
from shared.domain.types.user_id import UserId
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from shared.domain.value_objects.category_value_object import CategoryValueObject
from shared.domain.value_objects.money_value_object import MoneyValueObject
from budgeting.domain.entities.budget_allocation_entity import BudgetAllocationEntity
from budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)


class BudgetEntityProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    user_id: UserId
    allocations: list[BudgetAllocationEntity]
    budget_period: BudgetPeriodValueObject


class BudgetEntity(AggregateRoot[BudgetEntityProps]):
    """Aggregate root for budget."""

    def __init__(
        self,
        props: BudgetEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ):
        super().__init__(props, id, version)

    @property
    def user_id(self) -> UserId:
        return self.props["user_id"]

    @property
    def allocations(self) -> list[BudgetAllocationEntity]:
        return self.props["allocations"]

    @property
    def budget_period(self) -> BudgetPeriodValueObject:
        return self.props["budget_period"]

    def allocate_budget(
        self, allocation: BudgetAllocationEntity
    ) -> Either[None, DomainRuleError]:
        self._check_is_discarded_entity()

        if any(
            existing_allocation.category == allocation.category
            for existing_allocation in self.allocations
        ):
            return result_fail(
                DomainRuleError(None, "Budget allocation already exists")
            )

        self.props["allocations"].append(allocation)
        self._increment_version()
        return result_ok()

    def update_allocation(
        self,
        allocation_id: UniqueEntityId,
        *,
        amount: Decimal | None = None,
        currency: Currency | None = None,
        category: CategoryType | None = None,
    ) -> Either[None, DomainRuleError]:
        self._check_is_discarded_entity()

        for existing_allocation in self.allocations:
            if existing_allocation.id == allocation_id:
                if category is not None:
                    category_result = CategoryValueObject.create({"name": category})
                    if is_fail(category_result):
                        return result_fail(
                            DomainRuleError(
                                category_result.value, "Invalid category value"
                            )
                        )
                    existing_allocation.props["category"] = category_result.value

                if amount is not None or currency is not None:
                    money_result = MoneyValueObject.create(
                        {
                            "amount": (
                                MoneyValueObject.to_amount(amount)
                                if amount is not None
                                else existing_allocation.money.amount
                            ),
                            "currency": (
                                currency or existing_allocation.money.currency
                            ),
                        }
                    )

                    if is_fail(money_result):
                        return result_fail(
                            DomainRuleError(money_result.value, "Invalid money value")
                        )

                    existing_allocation.props["money"] = money_result.value

                self._increment_version()
                return result_ok()

        return result_fail(DomainRuleError(None, "Budget allocation not found"))

    def update_budget_period(
        self, start_date: date | None, end_date: date | None
    ) -> Either[None, DomainRuleError]:

        self._check_is_discarded_entity()
        if start_date is None and end_date is None:
            return result_fail(
                DomainRuleError(
                    Exception("Invalid budget period update"),
                    "At least one of start_date or end_date must be provided",
                )
            )

        budget_period_result = BudgetPeriodValueObject.create(
            {
                "start_date": start_date or self.budget_period.start_date,
                "end_date": end_date or self.budget_period.end_date,
            }
        )

        if is_fail(budget_period_result):
            return result_fail(
                DomainRuleError(budget_period_result.value, "Invalid budget period")
            )

        self.props["budget_period"] = budget_period_result.value
        self._increment_version()
        return result_ok()

    def remove_allocation(
        self, allocation_id: UniqueEntityId
    ) -> Either[BudgetAllocationEntity, DomainRuleError]:
        self._check_is_discarded_entity()

        for index, existing_allocation in enumerate(self.allocations):
            if existing_allocation.id == allocation_id:
                allocation = self.props["allocations"].pop(index)
                self._increment_version()
                return result_ok(allocation)

        return result_fail(DomainRuleError(None, "Budget allocation not found"))

    @classmethod
    def create(
        cls,
        props: BudgetEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))

    @classmethod
    def existing_user_entity(
        cls, props: BudgetEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))
