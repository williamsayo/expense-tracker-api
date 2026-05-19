import asyncio
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from boilerplate.errors.http import AuthenticationError
from result import is_fail, result_ok

from expenses.application.services.expense_service import ExpenseService
from expenses.domain.entities.expense_entity import ExpenseEntity
from expenses.infrastructure.adapters.dto.expense import (
    ExpenseUpdateModel,
    ExpenseWriteModel,
)
from shared.domain.types.category_types import Category
from shared.domain.types.currency_types import Currency
from shared.domain.types.user_id import UserId
from shared.domain.value_objects.category_value_object import CategoryValueObject
from shared.domain.value_objects.money_value_object import MoneyValueObject


def _build_expense(user_id: UserId | None = None) -> ExpenseEntity:
    category_result = CategoryValueObject.create({"name": Category.FOOD})
    money_result = MoneyValueObject.create({"amount": 1000, "currency": Currency.EUR})

    assert not is_fail(category_result)
    assert not is_fail(money_result)

    entity_result = ExpenseEntity.create(
        {
            "user_id": user_id or UserId(uuid4()),
            "category": category_result.value,
            "money": money_result.value,
            "note": "Lunch",
            "date": datetime(2026, 3, 21, 12, 0, 0),
        }
    )

    assert not is_fail(entity_result)
    return entity_result.value


def test_create_expense_usecase_persists_entity() -> None:
    repo = SimpleNamespace(add=AsyncMock(return_value=result_ok()))
    service = ExpenseService(SimpleNamespace(repo=repo))
    user_id = UserId(uuid4())

    write_model = ExpenseWriteModel(
        amount=Decimal("12.50"),
        currency=Currency.EUR,
        category=Category.FOOD,
        note="Lunch",
        date=datetime(2026, 3, 21, 10, 30, 0),
    )

    result = asyncio.run(service.create_expense_usecase(user_id, write_model))

    assert not is_fail(result)
    assert result.value.user_id == user_id
    assert result.value.money.amount == 1250
    repo.add.assert_awaited_once_with(result.value)


def test_update_expense_usecase_rejects_unauthorized_user() -> None:
    owner_user = UserId(uuid4())
    requester = UserId(uuid4())
    expense = _build_expense(owner_user)

    repo = SimpleNamespace(
        get_by_id=AsyncMock(return_value=result_ok(expense)),
        add=AsyncMock(return_value=result_ok()),
    )
    service = ExpenseService(SimpleNamespace(repo=repo))

    update_model = ExpenseUpdateModel(
        amount=Decimal("20.00"),
        currency=Currency.USD,
        category=Category.RENT,
        note="Updated",
        date=datetime(2026, 3, 22, 9, 0, 0),
    )

    result = asyncio.run(
        service.update_expense_usecase(str(expense.id.value), requester, update_model)
    )

    assert is_fail(result)
    assert isinstance(result.value, AuthenticationError)
    repo.add.assert_not_awaited()


def test_delete_expense_by_category_usecase_calls_repo_with_category_and_user() -> None:
    user_id = UserId(uuid4())
    repo = SimpleNamespace(remove_all=AsyncMock(return_value=result_ok(2)))
    service = ExpenseService(SimpleNamespace(repo=repo))

    result = asyncio.run(
        service.delete_expense_by_category_usecase(Category.FOOD, user_id)
    )

    assert not is_fail(result)
    repo.remove_all.assert_awaited_once_with(Category.FOOD.value, user_id)
