from typing import Self, TypedDict
from pydantic import BaseModel
from boilerplate.domain.value_object import ValueObject
from boilerplate.domain.rules.apply_rule import apply_rules
from boilerplate.errors.domain import DomainRuleError
from result import is_fail, result_ok, result_fail, Either

class ExampleValueObjectProps(TypedDict): ...

class ExampleValueObject(ValueObject[ExampleValueObjectProps]):
    """
    Value Object
    """
    def __init__(self, props: ExampleValueObjectProps):
        super().__init__(props)

    @classmethod
    def create(cls, props: ExampleValueObjectProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, BaseModel)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        else:
            return result_ok(cls(result.value))