from typing import Self, TypedDict
from decimal import Decimal
from boilerplate import ValueObject, DomainRuleError, apply_rules
from result import is_fail, result_ok, result_fail, Either
from src.spending.budgeting.domain.rules.amount_rule import AmountSchema


class AmountValueObjectProps(TypedDict):
    """Typed dictionary for Amount value object fields."""

    amount: int


class AmountValueObject(ValueObject[AmountValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: AmountValueObjectProps):
        super().__init__(props)

    @property
    def value(self) -> int:
        return self.props["amount"]

    def major_unit(self) -> float:
        return round(self.props["amount"] / 100, 2)

    @staticmethod
    def cents(amount: Decimal) -> int:
        return int(round(amount * 100))

    @classmethod
    def create(cls, props: AmountValueObjectProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, AmountSchema)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        return result_ok(cls(result.value))
