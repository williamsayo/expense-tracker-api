import asyncio
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from boilerplate.errors.http import AuthenticationError
from result import is_fail, result_ok

from budgeting.application.services.budget_service import BudgetService
from budgeting.domain.entities.budget_allocation_entity import (
    BudgetAllocationEntity,
)
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.domain.value_objects.budget_period_value_object import (
    BudgetPeriodValueObject,
)
from budgeting.infrastructure.adapters.dto.budget import (
    BudgetUpdateModel,
    BudgetWriteModel,
)
from budgeting.infrastructure.adapters.dto.budget_allocation import (
    BudgetAllocationWriteModel,
)
from shared.domain.types.category_types import Category
from shared.domain.types.currency_types import Currency
from shared.domain.types.user_id import UserId
from shared.domain.value_objects.category_value_object import CategoryValueObject
from shared.domain.value_objects.money_value_object import MoneyValueObject


def _build_allocation(category: Category, amount: int) -> BudgetAllocationEntity:
    category_result = CategoryValueObject.create({"name": category})
    money_result = MoneyValueObject.create({"amount": amount, "currency": Currency.EUR})

    assert not is_fail(category_result)
    assert not is_fail(money_result)

    allocation_result = BudgetAllocationEntity.create(
        {"category": category_result.value, "money": money_result.value}
    )

    assert not is_fail(allocation_result)
    return allocation_result.value


def _build_budget(user_id: UserId | None = None) -> BudgetEntity:
    period_result = BudgetPeriodValueObject.create(
        {"start_date": date(2026, 3, 1), "end_date": date(2026, 3, 31)}
    )
    assert not is_fail(period_result)

    budget_result = BudgetEntity.create(
        {
            "user_id": user_id or UserId(uuid4()),
            "allocations": [_build_allocation(Category.FOOD, 10000)],
            "budget_period": period_result.value,
        }
    )

    assert not is_fail(budget_result)
    return budget_result.value


def test_create_budget_usecase_persists_budget() -> None:
    repo = SimpleNamespace(add=AsyncMock(return_value=result_ok()))
    service = BudgetService(SimpleNamespace(repo=repo))
    user_id = UserId(uuid4())

    write_model = BudgetWriteModel(
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 30),
        allocations=[
            {
                "amount": Decimal("100.00"),
                "currency": Currency.EUR,
                "category": Category.FOOD,
            }
        ],
    )

    result = asyncio.run(service.create_budget_usecase(user_id, write_model))

    assert not is_fail(result)
    assert result.value.user_id == user_id
    assert len(result.value.allocations) == 1
    repo.add.assert_awaited_once_with(result.value)


def test_add_budget_allocation_usecase_rejects_unauthorized_user() -> None:
    budget_owner = UserId(uuid4())
    requesting_user = UserId(uuid4())
    budget = _build_budget(budget_owner)

    repo = SimpleNamespace(
        get_by_id=AsyncMock(return_value=result_ok(budget)),
        add=AsyncMock(return_value=result_ok()),
    )
    service = BudgetService(SimpleNamespace(repo=repo))

    allocation_data = BudgetAllocationWriteModel(
        amount=Decimal("20.00"),
        currency=Currency.EUR,
        category=Category.RENT,
    )

    result = asyncio.run(
        service.add_budget_allocation_usecase(
            str(budget.id.value), requesting_user, allocation_data
        )
    )

    assert is_fail(result)
    assert isinstance(result.value, AuthenticationError)
    repo.add.assert_not_awaited()


def test_update_budget_usecase_updates_allocation_and_period() -> None:
    user_id = UserId(uuid4())
    budget = _build_budget(user_id)
    allocation_id = str(budget.allocations[0].id.value)

    repo = SimpleNamespace(
        get_by_id=AsyncMock(return_value=result_ok(budget)),
        add=AsyncMock(return_value=result_ok()),
    )
    service = BudgetService(SimpleNamespace(repo=repo))

    update_model = BudgetUpdateModel(
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 30),
        allocation={
            "id": allocation_id,
            "amount": Decimal("150.00"),
            "currency": Currency.USD,
            "category": Category.TRANSPORT,
        },
    )

    result = asyncio.run(
        service.update_budget_usecase(str(budget.id.value), user_id, update_model)
    )

    assert not is_fail(result)
    assert budget.allocations[0].money.amount == 15000
    assert budget.allocations[0].money.currency == Currency.USD
    assert budget.allocations[0].category.name == Category.TRANSPORT
    assert budget.budget_period.start_date == date(2026, 4, 1)
    assert budget.budget_period.end_date == date(2026, 4, 30)
    repo.add.assert_awaited_once_with(budget)
