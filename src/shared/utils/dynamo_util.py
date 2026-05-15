from functools import reduce
from typing import Any, Mapping
from aiodynamo.expressions import F, UpdateExpression, Condition


def build_update_expression(fields: Mapping[str, Any]) -> UpdateExpression:
    expression = reduce(
        lambda a, b: a & b, [F(key).set(value) for key, value in fields.items()]
    )

    update_expr = expression & F("version").add(1)

    return update_expr


def build_condition(fields: Mapping[str, Any]) -> Condition:
    condition = reduce(
        lambda a, b: a & b, [F(key).equals(value) for key, value in fields.items()]
    )

    return condition
