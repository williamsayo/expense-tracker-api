from typing import Self, TypedDict
from decimal import Decimal
from boilerplate.domain.value_object import ValueObject
from boilerplate.domain.rules.apply_rule import apply_rules
from boilerplate.errors.domain import DomainRuleError
from result import is_fail, result_ok, result_fail, Either
from shared.domain.rules.money_rule import MoneySchema
from shared.domain.types.currency_types import Currency, currency_display


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

    def to_currency(self) -> str:
        currency = currency_display.get(self.currency)
        return f'{currency}{self.props["amount"]/100:.2f}'

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
