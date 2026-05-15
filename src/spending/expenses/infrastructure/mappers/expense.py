from datetime import datetime
from typing import cast
from uuid import UUID
from boilerplate import (
    BaseMapper,
    CoreError,
    UniqueEntityId,
    IllegalArgumentError,
    CoreError,
)
from result import result_ok, result_fail, Either, is_fail, result_combine
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.repositories.schema import (
    ExpenseSchema,
)
from aiodynamo.types import Item


def create_unique_entity_id(id: str | UUID) -> Either[UniqueEntityId, CoreError]:
    try:
        return result_ok(UniqueEntityId(id))
    except Exception as error:
        return result_fail(IllegalArgumentError(error, "Invalid Expense ID"))


class ExpenseMapper(BaseMapper):
    """Maps expense data between domain and persistence models."""

    @staticmethod
    def to_persistence(entity: ExpenseEntity) -> Item:
        date = entity.date.isoformat()

        persistence: ExpenseSchema = {
            "id": entity.id.to_string(),
            "name": entity.name,
            "auth_id": str(entity.auth_id),
            "budget_id": (str(entity.budget_id) if entity.budget_id else "UNBUDGETED"),
            "amount": entity.money.amount,
            "currency": entity.money.currency.value,
            "category": entity.category.name.value,
            "date": date,
            "note": entity.note,
            "version": entity.version,
        }

        return cast(Item, persistence)

    @staticmethod
    def to_domain(persistence: Item) -> Either[ExpenseEntity, CoreError]:
        id_result = create_unique_entity_id(persistence["id"])

        money_result = MoneyValueObject.create(
            {
                "amount": persistence["amount"],
                "currency": Currency(persistence["currency"]),
            }
        )
        category_result = CategoryValueObject.create({"name": persistence["category"]})

        combined_result = result_combine((id_result, money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, money, category = combined_result.value

        return ExpenseEntity.existing_entity(
            {
                "name": persistence["name"],
                "auth_id": UUID(persistence["auth_id"]),
                "date": datetime.fromisoformat(persistence["date"]),
                "note": persistence["note"],
                "category": category,
                "money": money,
            },
            id=entity_id,
            version=persistence["version"],
        )
