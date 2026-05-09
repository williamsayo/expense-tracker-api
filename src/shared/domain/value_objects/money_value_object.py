from typing import Self, TypedDict
from decimal import Decimal
from boilerplate import ValueObject, DomainRuleError, apply_rules
from result import is_fail, result_ok, result_fail, Either
from src.shared.domain.rules.money_rule import MoneySchema
from src.shared.domain.types.currency_types import Currency, currency_display


class MoneyValueObjectProps(TypedDict):
    """Typed dictionary for money value object fields."""

    amount: int
    currency: Currency


class MoneyValueObject(ValueObject[MoneyValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: MoneyValueObjectProps):
        super().__init__(props)

    @property
    def currency(self) -> Currency:
        return self.props["currency"]

    @property
    def amount(self) -> int:
        return self.props["amount"]

    def to_currency(self) -> float:
        return self.props["amount"] / 100

    @staticmethod
    def to_amount(amount: Decimal) -> int:
        return int(round(amount * 100))

    @classmethod
    def create(cls, props: MoneyValueObjectProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, MoneySchema)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        return result_ok(cls(result.value))

    @staticmethod
    def format_currency(value: str):
        return value.strip().upper()
