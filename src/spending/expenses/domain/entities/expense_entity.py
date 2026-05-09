from typing import NotRequired, TypedDict, Self, Never
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from result import is_fail, result_ok, Either
from boilerplate import (
    AggregateRoot,
    UniqueEntityId,
    DomainRuleError,
)
from shared.domain.value_objects.money_value_object import MoneyValueObject
from shared.domain.value_objects.category_value_object import CategoryValueObject
from shared.domain.types.user_id import UserId
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from spending.expenses.domain.events.expense_created import ExpenseCreated


class ExpenseEntityProps(TypedDict):
    """Typed dictionary for expense entity fields."""

    name: str | None
    user_id: UserId
    budget_id: NotRequired[UUID | str]
    category: CategoryValueObject
    money: MoneyValueObject
    note: str | None
    date: datetime


class ExpenseEntity(AggregateRoot[ExpenseEntityProps]):
    """Aggregate root for expense."""

    def __init__(
        self,
        props: ExpenseEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ):
        super().__init__(props, id, version)

    @property
    def name(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["name"]

    @property
    def user_id(self) -> UserId:
        self._check_is_discarded_entity()
        return self.props["user_id"]

    @property
    def category(self) -> CategoryValueObject:
        self._check_is_discarded_entity()
        return self.props["category"]

    @property
    def money(self) -> MoneyValueObject:
        self._check_is_discarded_entity()
        return self.props["money"]

    @property
    def note(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["note"]

    @property
    def date(self) -> datetime:
        self._check_is_discarded_entity()
        return self.props["date"]

    @property
    def budget_id(self) -> UUID | str | None:
        self._check_is_discarded_entity()
        return self.props.get("budget_id")

    def assign_to_budget(self, budget_id: UUID | str) -> None:
        self._check_is_discarded_entity()
        self.props["budget_id"] = budget_id

    def update_expense(
        self,
        amount: Decimal | None,
        category: CategoryType | None,
        currency: Currency | None,
        note: str | None,
        date: datetime | None,
        name: str | None,
    ) -> Either[None, DomainRuleError]:
        self._check_is_discarded_entity()
        if amount is not None or currency is not None:
            amount_value_object = (
                MoneyValueObject.to_amount(amount)
                if amount is not None
                else self.props["money"].amount
            )
            money_result = MoneyValueObject.create(
                {
                    "amount": amount_value_object,
                    "currency": currency or self.props["money"].currency,
                }
            )

            if is_fail(money_result):
                return money_result

            self.props["money"] = money_result.value

        if category is not None:
            category_result = CategoryValueObject.create({"name": category})

            if is_fail(category_result):
                return category_result

            self.props["category"] = category_result.value

        if note is not None:
            self.props["note"] = note

        if date is not None:
            self.props["date"] = date

        if name is not None:
            self.props["name"] = name

        self._increment_version()
        return result_ok()

    @classmethod
    def create(
        cls,
        props: ExpenseEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        entity = cls(props, id, version)
        entity.apply(
            ExpenseCreated.create_event(
                {
                    "expense_id": entity.id.value,
                    "user_id": entity.user_id,
                    "category": entity.category.name,
                    "amount": entity.money.amount,
                    "currency": entity.money.currency,
                    "date": entity.date,
                },
                metadata={
                    "aggregate_type": cls.__name__,
                    "version": entity.version,
                },
            )
        )
        return result_ok(entity)

    @classmethod
    def existing_entity(
        cls, props: ExpenseEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))
