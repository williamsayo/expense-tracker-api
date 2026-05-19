from datetime import date
from decimal import Decimal
from uuid import uuid4

from result import is_fail

from src.budgeting.domain.entities.budget_allocation_entity import (
    BudgetAllocationEntity,
)
from src.budgeting.domain.entities.budget_entity import BudgetEntity
from src.budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.types.user_id import UserId
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject


def _build_allocation(category: Category, amount: int) -> BudgetAllocationEntity:
    category_result = CategoryValueObject.create({"name": category})
    money_result = MoneyValueObject.create({"amount": amount, "currency": Currency.EUR})

    assert not is_fail(category_result)
    assert not is_fail(money_result)

    allocation_result = BudgetAllocationEntity.create(
        {"money": money_result.value, "category": category_result.value}
    )

    assert not is_fail(allocation_result)
    return allocation_result.value


def _build_budget() -> BudgetEntity:
    period_result = BudgetPeriodValueObject.create(
        {"start_date": date(2026, 3, 1), "end_date": date(2026, 3, 31)}
    )

    assert not is_fail(period_result)

    budget_result = BudgetEntity.create(
        {
            "user_id": UserId(uuid4()),
            "allocations": [_build_allocation(Category.FOOD, 10000)],
            "budget_period": period_result.value,
        }
    )

    assert not is_fail(budget_result)
    return budget_result.value


def test_budget_period_rejects_equal_or_earlier_end_date() -> None:
    result = BudgetPeriodValueObject.create(
        {"start_date": date(2026, 3, 10), "end_date": date(2026, 3, 10)}
    )

    assert is_fail(result)


def test_allocate_budget_rejects_duplicate_category() -> None:
    budget = _build_budget()
    duplicate_allocation = _build_allocation(Category.FOOD, 12000)

    result = budget.allocate_budget(duplicate_allocation)

    assert is_fail(result)
    assert len(budget.allocations) == 1


def test_update_allocation_changes_money_and_version() -> None:
    budget = _build_budget()
    allocation_id = budget.allocations[0].id

    result = budget.update_allocation(
        allocation_id,
        amount=Decimal("150.00"),
        currency=Currency.USD,
    )

    assert not is_fail(result)
    assert budget.allocations[0].money.amount == 15000
    assert budget.allocations[0].money.currency == Currency.USD
    assert budget.version == 1
