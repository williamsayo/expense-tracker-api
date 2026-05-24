from uuid import UUID
from boilerplate import (
    BaseMapper,
    CoreError,
    UniqueEntityId,
    IllegalArgumentError,
    CoreError,
)
from result import result_ok, result_fail, Either, is_fail, result_combine
from src.shared.domain.value_objects.category_value_object import CategoryValueObject
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.repositories.schema import Expense


def create_unique_entity_id(id: str | UUID) -> Either[UniqueEntityId, CoreError]:
    try:
        return result_ok(UniqueEntityId(id))
    except Exception as error:
        return result_fail(IllegalArgumentError(error, "Invalid Expense ID"))


class ExpenseMapper(BaseMapper):
    """Maps expense data between domain and persistence models."""

    @staticmethod
    def to_persistence(entity: ExpenseEntity) -> Expense:
        return Expense(
            id=entity.id.value,
            name=entity.name,
            merchant=entity.merchant,
            user_id=entity.user_id,
            budget_id=entity.budget_id,
            amount=entity.money.amount,
            currency=entity.money.currency,
            category=entity.category.name,
            date=entity.date,
            note=entity.note,
            receipt_url=entity.receipt,
            version=entity.version,
        )

    @staticmethod
    def to_domain(persistence: Expense) -> Either[ExpenseEntity, CoreError]:
        id_result = create_unique_entity_id(persistence.id)

        money_result = MoneyValueObject.create(
            {"amount": persistence.amount, "currency": persistence.currency}
        )
        category_result = CategoryValueObject.create({"name": persistence.category})

        combined_result = result_combine((id_result, money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, money, category = combined_result.value

        return ExpenseEntity.existing_entity(
            {
                "name": persistence.name,
                "user_id": persistence.user_id,
                "date": persistence.date,
                "note": persistence.note,
                "category": category,
                "money": money,
                "merchant": persistence.merchant,
                "receipt": persistence.receipt_url,
            },
            id=entity_id,
            version=persistence.version,
        )
