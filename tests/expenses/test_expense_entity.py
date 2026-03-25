from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from result import is_fail

from src.expenses.domain.entities.expense_entity import ExpenseEntity
from src.shared.domain.types.category_types import CategoryType
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.types.user_id import UserId
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject


def _build_expense() -> ExpenseEntity:
    category_result = CategoryValueObject.create({"name": CategoryType.FOOD})
    money_result = MoneyValueObject.create({"amount": 1000, "currency": Currency.EUR})

    assert not is_fail(category_result)
    assert not is_fail(money_result)

    expense_result = ExpenseEntity.create(
        {
            "user_id": UserId(uuid4()),
            "category": category_result.value,
            "money": money_result.value,
            "note": "Lunch",
            "date": datetime(2026, 3, 21),
        }
    )

    assert not is_fail(expense_result)
    return expense_result.value


def test_update_expense_updates_fields_and_increments_version() -> None:
    expense = _build_expense()

    result = expense.update_expense(
        amount=Decimal("12.50"),
        category=CategoryType.RENT,
        currency=Currency.USD,
        note="Updated",
        date=datetime(2026, 3, 22),
    )

    assert not is_fail(result)
    assert expense.money.amount == 1250
    assert expense.money.currency == Currency.USD
    assert expense.category.name == CategoryType.RENT
    assert expense.note == "Updated"
    assert expense.date == datetime(2026, 3, 22)
    assert expense.version == 1


def test_update_expense_returns_fail_for_invalid_amount() -> None:
    expense = _build_expense()

    result = expense.update_expense(
        amount=Decimal("0.10"),
        category=None,
        currency=Currency.EUR,
        note=None,
        date=None,
    )

    assert is_fail(result)
    assert expense.money.amount == 1000
    assert expense.version == 0
