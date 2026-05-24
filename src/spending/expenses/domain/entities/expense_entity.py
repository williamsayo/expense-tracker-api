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
from src.shared.domain.value_objects.media_value_object import MediaValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.types.user_id import UserId
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency
from src.spending.expenses.domain.events.expense_created import ExpenseCreated


class ExpenseEntityProps(TypedDict):
    """Typed dictionary for expense entity fields."""

    name: str | None
    merchant: str | None
    user_id: UserId
    budget_id: NotRequired[UUID | str]
    category: CategoryValueObject
    money: MoneyValueObject
    note: str | None
    date: datetime
    receipt: str | None


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
    def merchant(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["merchant"]

    @property
    def receipt(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["receipt"]

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
        category: Category | None,
        currency: Currency | None,
        note: str | None,
        date: datetime | None,
        name: str | None,
        merchant: str | None,
    ) -> Either[None, DomainRuleError]:
        self._check_is_discarded_entity()

        if amount is not None or currency is not None:
            amount_cents = (
                MoneyValueObject.cents(amount)
                if amount is not None
                else self.money.amount
            )
            self._update_money(
                amount=amount_cents,
                currency=currency or self.money.currency,
            )

        if category is not None:
            self._update_category(category)

        if date is not None:
            self._update_date(date)

        if note is not None:
            self.props["note"] = note

        if name is not None:
            self.props["name"] = name

        if merchant is not None:
            self.props["merchant"] = merchant

        self._increment_version()
        return result_ok()

    def update_receipt(
        self, receipt_key: str, url: str
    ) -> Either[None, DomainRuleError]:
        receipt_value_object = MediaValueObject.create(
            {"file_key": receipt_key, "file_url": url}
        )

        if is_fail(receipt_value_object):
            return receipt_value_object

        self.props["receipt"] = receipt_value_object.value.key

        return result_ok()

    def _update_date(self, date: datetime) -> None:
        self.props["date"] = date

    def _update_category(self, category: Category) -> None:
        category_result = CategoryValueObject.create({"name": category})

        if is_fail(category_result):
            raise ValueError(f"Invalid category: {category}")

        self.props["category"] = category_result.value

    def _update_money(self, amount: int, currency: Currency) -> None:
        money_result = MoneyValueObject.create(
            {
                "amount": amount,
                "currency": currency,
            }
        )

        if is_fail(money_result):
            raise ValueError(f"Invalid amount or currency: {amount} {currency}")

        self.props["money"] = money_result.value

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
                    "expense_id": entity.id.to_string(),
                    "user_id": str(entity.user_id),
                    "name": entity.name,
                    "merchant": "adereal",  # TODO: remove merchant field in future
                    "category": entity.category.name.value,
                    "amount": entity.money.amount,
                    "currency": entity.money.currency.value,
                    "date": entity.date.isoformat(),
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
