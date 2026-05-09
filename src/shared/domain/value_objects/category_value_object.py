from typing import Self, TypedDict
from boilerplate.domain.value_object import ValueObject
from boilerplate.domain.rules.apply_rule import apply_rules
from boilerplate.errors.domain import DomainRuleError
from result import is_fail, result_ok, result_fail, Either
from src.shared.domain.rules.category_rule import CategorySchema
from src.shared.domain.types.category_types import CategoryType


class CategoryValueObjectProps(TypedDict):
    """Typed dictionary for category value object fields."""
    name: CategoryType


class CategoryValueObject(ValueObject[CategoryValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: CategoryValueObjectProps):
        super().__init__(props)

    @property
    def name(self) -> CategoryType:
        return self.props["name"]

    @classmethod
    def create(cls, props: CategoryValueObjectProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, CategorySchema)
        if is_fail(result):
            return result_fail(DomainRuleError(result.value))
        return result_ok(cls(result.value))