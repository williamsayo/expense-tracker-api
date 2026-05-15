from typing import Any, TypeVar, cast

T = TypeVar("T")


def typed(item: dict[str, Any]) -> T:
    return cast(T, item)
