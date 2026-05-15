from typing import TypedDict
from datetime import datetime
from uuid import UUID
from src.shared.domain.types.category_types import CategoryType
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.types.user_id import UserId


class ExpenseReadModelProps(TypedDict):
    """Typed dictionary for expense read model fields."""

    id: UUID
    name: str | None
    auth_id: UUID
    category: CategoryType
    amount: float
    currency: Currency
    note: str | None
    date: datetime


class ExpenseReadModel:
    """Read model for expense read model."""

    def __init__(
        self,
        props: ExpenseReadModelProps,
    ):
        self._id = props["id"]
        self._name = props["name"]
        self._auth_id = props["auth_id"]
        self._category = props["category"]
        self._amount = props["amount"]
        self._currency = props["currency"]
        self._note = props["note"]
        self._date = props["date"]

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def auth_id(self) -> UUID:
        return self._auth_id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def amount(self) -> float:
        return self._amount / 100

    @property
    def category(self) -> CategoryType:
        return self._category

    @property
    def note(self) -> str | None:
        return self._note
