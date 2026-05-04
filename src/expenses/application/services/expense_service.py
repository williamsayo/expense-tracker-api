from fastapi import BackgroundTasks
from typing import Sequence, List
from result import result_ok, result_fail, is_fail, Either, result_combine
from boilerplate import (
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    AuthenticationError,
    ApplicationErrorID,
    DomainRuleError,
    CoreError,
)
from shared.application.services.base import BaseService
from shared.domain.value_objects.category_value_object import CategoryValueObject
from shared.domain.value_objects.money_value_object import MoneyValueObject
from shared.domain.types.category_types import CategoryType
from shared.domain.types.user_id import UserId
from expenses.utils.setup_dependencies import ExpenseDeps
from expenses.domain.entities.expense_entity import ExpenseEntity
from expenses.infrastructure.mappers.expense_mapper import create_unique_entity_id
from expenses.infrastructure.adapters.dto.expense import (
    ExpenseWriteModel,
    ExpenseUpdateModel,
)


class ExpenseService(BaseService[ExpenseDeps]):
    """Service layer."""

    def __init__(
        self,
        deps: ExpenseDeps,
    ):
        super().__init__(deps)

    async def create_expense_usecase(
        self,
        user_id: UserId,
        expense_data: ExpenseWriteModel,
        background_tasks: BackgroundTasks,
    ) -> Either[
        ExpenseEntity,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        amount = MoneyValueObject.to_amount(expense_data.amount)
        money_result = MoneyValueObject.create(
            {"amount": amount, "currency": expense_data.currency}
        )
        category_result = CategoryValueObject.create({"name": expense_data.category})

        combined_result = result_combine((money_result, category_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        money, category = combined_result.value

        entity_result = ExpenseEntity.create(
            {
                "name": expense_data.name,
                "user_id": user_id,
                "category": category,
                "money": money,
                "date": expense_data.date,
                "note": expense_data.note,
            }
        )

        result = await self.deps.repo.add(entity_result.value)

        if is_fail(result):
            return result

        # Dispatch uncommitted events after successful persistence
        events = entity_result.value.uncommited_events
        background_tasks.add_task(self.deps.dispatcher.publish_all, events)
        entity_result.value.uncommit()

        return entity_result

    async def update_expense_usecase(
        self, aggregate_id: str, user_id: UserId, expense_data: ExpenseUpdateModel
    ) -> Either[
        ExpenseEntity,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError
        | DomainRuleError,
    ]:
        entity_id = create_unique_entity_id(aggregate_id)

        if is_fail(entity_id):
            return entity_id

        result = await self.deps.repo.get_by_id(entity_id.value)

        if is_fail(result):
            return result

        entity = result.value

        if entity.user_id != user_id:
            return result_fail(
                AuthenticationError(
                    ApplicationErrorID.AUTHENTICATION,
                    "You do not have permission to update this expense",
                )
            )

        update_result = entity.update_expense(
            amount=expense_data.amount,
            category=expense_data.category,
            currency=expense_data.currency,
            note=expense_data.note,
            date=expense_data.date,
            name=expense_data.name,
        )

        if is_fail(update_result):
            return update_result

        result = await self.deps.repo.add(entity)

        if is_fail(result):
            return result

        return result_ok(entity)

    async def delete_expense_usecase(
        self, aggregateId: str, user_id: UserId
    ) -> Either[None, RepositoryUnexpectedError | CoreError]:

        id_result = create_unique_entity_id(aggregateId)

        if is_fail(id_result):
            return result_fail(id_result.value)

        entity_result = await self.deps.repo.get_by_id(id_result.value)

        if is_fail(entity_result):
            return result_fail(entity_result.value)

        entity = entity_result.value

        if entity.user_id != user_id:
            return result_fail(
                AuthenticationError(
                    ApplicationErrorID.AUTHENTICATION,
                    "You do not have permission to delete this expense",
                )
            )

        result = await self.deps.repo.remove(entity)

        if is_fail(result):
            return result_fail(result.value)

        return result_ok()

    async def delete_expense_by_category_usecase(
        self, category: CategoryType, user_id: UserId
    ) -> Either[
        None,
        RepositoryUnexpectedError | AuthenticationError | CoreError,
    ]:
        result = await self.deps.repo.remove_all(category.value, user_id)

        if is_fail(result):
            return result_fail(result.value)

        return result_ok()
