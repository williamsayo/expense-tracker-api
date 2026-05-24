from uuid import UUID

from fastapi import BackgroundTasks
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
from src.shared.application.dtos.upload import FileUploadDTO
from src.shared.application.services.base import BaseService
from src.shared.domain.types.category_types import Category
from src.spending.expenses.utils.setup_dependencies import ExpenseDeps
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.mappers.expense_mapper import (
    create_unique_entity_id,
)
from src.spending.expenses.infrastructure.adapters.dto.expense import (
    ExpenseUpdateModel,
)


class ExpenseService(BaseService[ExpenseDeps]):
    """Service layer."""

    def __init__(
        self,
        deps: ExpenseDeps,
    ):
        super().__init__(deps)

    async def update_expense_usecase(
        self,
        aggregate_id: str,
        user_id: UUID,
        expense_data: ExpenseUpdateModel,
        receipt: FileUploadDTO | None,
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

        if receipt is not None:
            receipt_key_result = await self.deps.object_storage.upload_receipt(
                receipt.filename,
                receipt.file.file,
                content_type=receipt.content_type,
                user_id=str(user_id),
            )

            if is_fail(receipt_key_result):
                return result_fail(receipt_key_result.value)

            receipt_key = receipt_key_result.value

            url = self.deps.cdn.generate_url(receipt_key)

            receipt_update_result = entity.update_receipt(receipt_key, url)

            if is_fail(receipt_update_result):
                return receipt_update_result

        update_result = entity.update_expense(
            amount=expense_data.amount,
            category=expense_data.category,
            currency=expense_data.currency,
            note=expense_data.note,
            date=expense_data.date,
            name=expense_data.name,
            merchant=expense_data.merchant,
        )

        if is_fail(update_result):
            return update_result

        result = await self.deps.repo.add(entity)

        if is_fail(result):
            return result

        return result_ok(entity)

    async def delete_expense_usecase(
        self, aggregateId: str, user_id: UUID
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
        self, category: Category, user_id: UUID
    ) -> Either[
        None,
        RepositoryUnexpectedError | AuthenticationError | CoreError,
    ]:
        result = await self.deps.repo.remove_all(category.value, user_id)

        if is_fail(result):
            return result_fail(result.value)

        return result_ok()
