from typing import TypedDict

from result import Either, is_fail, result_fail, result_ok
from boilerplate import (
    ApplicationErrorID,
    AuthenticationError,
    CoreError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncQueryUseCase,
)
from src.shared.domain.types.user_id import UserId
from src.spending.expenses.infrastructure.mappers.expense_mapper import (
    create_unique_entity_id,
)
from src.spending.expenses.domain.read_models.expense_read_model import ExpenseReadModel
from src.spending.expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseInput(TypedDict):
    aggregate_id: str
    user_id: UserId


class GetExpenseUsecase(AsyncQueryUseCase[GetExpenseInput, ExpenseReadModel]):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, input: GetExpenseInput) -> Either[
        ExpenseReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        entity_id = create_unique_entity_id(input["aggregate_id"])

        if is_fail(entity_id):
            return entity_id

        unique_entity_id = entity_id.value

        result = await self.deps.repo.get_by_id(unique_entity_id.value)

        if is_fail(result):
            return result

        entity = result.value

        if entity.user_id != input["user_id"]:
            return result_fail(
                AuthenticationError(
                    ApplicationErrorID.AUTHENTICATION,
                    "You do not have permission to view this expense",
                )
            )

        return result_ok(result.value)
