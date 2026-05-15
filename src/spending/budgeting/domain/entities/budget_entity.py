from decimal import Decimal
from typing import Never, NotRequired, TypedDict, Self
from datetime import date
from uuid import UUID
from boilerplate import DomainRuleError, AggregateRoot, UniqueEntityId
from result import Either, is_fail, result_fail, result_ok
from src.shared.domain.types.category_types import CategoryType
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.budgeting.domain.value_objects.amount_value_object import (
    AmountValueObject,
)
from src.spending.budgeting.domain.entities.budget_allocation_entity import (
    BudgetAllocationEntity,
)
from src.spending.budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from src.spending.budgeting.domain.events.budget_created import BudgetCreated
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity


class BudgetEntityProps(TypedDict):
    """Typed dictionary for budget entity fields."""

    name: str | None
    auth_id: UUID
    allocations: list[BudgetAllocationEntity]
    currency: Currency
    budget_period: BudgetPeriodValueObject
    expenses: NotRequired[list[ExpenseEntity]]


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
    def name(self) -> str | None:
        return self.props["name"]

    @property
    def auth_id(self) -> UUID:
        return self.props["auth_id"]

    @property
    def currency(self) -> Currency:
        return self.props["currency"]

    @property
    def allocations(self) -> list[BudgetAllocationEntity]:
        return self.props["allocations"]

    @property
    def budget_period(self) -> BudgetPeriodValueObject:
        return self.props["budget_period"]

    @property
    def expenses(self) -> list[ExpenseEntity]:
        return self.props.get("expenses", [])

    def track_expense(
        self, category: CategoryValueObject, money: MoneyValueObject
    ) -> None:
        self._check_is_discarded_entity()
        for allocation in self.allocations:
            if allocation.category == category:
                allocation.apply_spending(money.to_currency())

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

        existing_allocation = next(
            (
                allocation
                for allocation in self.allocations
                if allocation.id == allocation_id
            ),
            None,
        )

        if existing_allocation is None:
            return result_fail(DomainRuleError(None, "Budget allocation not found"))

        if category is not None:
            category_result = CategoryValueObject.create({"name": category})

            if is_fail(category_result):
                return result_fail(
                    DomainRuleError(category_result.value, "Invalid category value")
                )

            existing_allocation.props["category"] = category_result.value

        if amount is not None or currency is not None:
            money_result = AmountValueObject.create(
                {
                    "amount": (
                        AmountValueObject.to_amount(amount)
                        if amount is not None
                        else existing_allocation.amount.value
                    ),
                }
            )

            if is_fail(money_result):
                return result_fail(
                    DomainRuleError(money_result.value, "Invalid money value")
                )

            existing_allocation.props["amount"] = money_result.value

        return result_ok()

    def change_budget_context(
        self, currency: Currency | None, start_date: date | None, end_date: date | None
    ) -> Either[None, DomainRuleError]:
        self._check_is_discarded_entity()

        if all(field is None for field in (start_date, end_date, currency)):
            return result_ok()

        if currency is not None:
            self._change_currency(currency)

        if start_date is not None or end_date is not None:
            budget_period_result = self._update_budget_period(
                start_date=start_date, end_date=end_date
            )

            if is_fail(budget_period_result):
                return result_fail(budget_period_result.value)

        return result_ok()

    def _change_currency(self, currency: Currency) -> None:
        self.props["currency"] = currency

    def _update_budget_period(
        self, start_date: date | None, end_date: date | None
    ) -> Either[None, DomainRuleError]:
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
        return result_ok()

    def remove_allocation(
        self, allocation_id: UniqueEntityId
    ) -> Either[BudgetAllocationEntity, DomainRuleError]:
        self._check_is_discarded_entity()

        for index, existing_allocation in enumerate(self.allocations):
            if existing_allocation.id == allocation_id:
                existing_allocation.discard()
                allocation = self.props["allocations"].pop(index)
                return result_ok(allocation)

        return result_fail(DomainRuleError(None, "Budget allocation not found"))

    @classmethod
    def create(
        cls,
        props: BudgetEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        entity = cls(props, id, version)

        entity.apply(
            BudgetCreated.create_event(
                {
                    "auth_id": str(entity.auth_id),
                    "name": entity.name,
                    "allocations": [
                        {
                            "allocation_id": allocation.id.value,
                            "budget_amount": allocation.amount.value,
                            "category": allocation.category.name,
                        }
                        for allocation in entity.allocations
                    ],
                    "start_date": entity.budget_period.start_date,
                    "end_date": entity.budget_period.end_date,
                    "currency": entity.currency,
                    "budget_id": str(entity.id.value),
                },
            )
        )
        return result_ok(entity)

    @classmethod
    def existing_user_entity(
        cls, props: BudgetEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))
