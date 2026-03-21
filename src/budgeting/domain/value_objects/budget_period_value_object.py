from typing import Self, TypedDict
from datetime import date
from pydantic import BaseModel
from boilerplate.domain.value_object import ValueObject
from boilerplate.domain.rules.apply_rule import apply_rules
from boilerplate.errors.domain import DomainRuleError
from result import is_fail, result_ok, result_fail, Either


class BudgetPeriodValueObjectProps(TypedDict):
    """Typed dictionary for date value object fields."""

    start_date: date
    end_date: date


class BudgetPeriodValueObject(ValueObject[BudgetPeriodValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: BudgetPeriodValueObjectProps):
        super().__init__(props)

    @property
    def start_date(self) -> date:
        return self.props["start_date"]

    @property
    def end_date(self) -> date:
        return self.props["end_date"]

    @classmethod
    def create(
        cls, props: BudgetPeriodValueObjectProps
    ) -> Either[Self, DomainRuleError]:
        if props["end_date"] <= props["start_date"]:
            return result_fail(
                DomainRuleError(
                    None, "end_date cannot be less than or equal to start_date"
                )
            )
        # result = apply_rules(props, BaseModel)
        # if is_fail(result):
        #     return result_fail(DomainRuleError(result.value))
        return result_ok(cls(props))
