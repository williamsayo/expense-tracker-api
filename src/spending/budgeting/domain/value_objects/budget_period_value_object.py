from typing import Self, TypedDict
from datetime import date
from boilerplate import ValueObject, apply_rules, DomainRuleError
from result import is_fail, result_ok, result_fail, Either
from src.spending.budgeting.domain.rules.budget_period_rules import BudgetPeriodSchema


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
        result = apply_rules(props, BudgetPeriodSchema)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        return result_ok(cls(props))
