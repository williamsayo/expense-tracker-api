from typing import Self, TypedDict
from result import is_fail, result_ok, result_fail, Either
from boilerplate.domain.value_object import ValueObject
from boilerplate.domain.rules.apply_rule import apply_rules
from boilerplate.errors.domain import DomainRuleError
from src.identity.domain.rules.email_address import EmailSchema


class EmailProps(TypedDict):
    """Typed dictionary for email fields."""

    value: str


class EmailValueObject(ValueObject[EmailProps]):
    """Value object representing email."""

    def __init__(self, props: EmailProps):
        super().__init__(props)

    @property
    def value(self) -> str:
        return self.props["value"]

    @classmethod
    def create(cls, props: EmailProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, EmailSchema)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        return result_ok(cls({"value": EmailValueObject.format(result.value["value"])}))

    @staticmethod
    def format(email: str) -> str:
        return email.strip().lower()
