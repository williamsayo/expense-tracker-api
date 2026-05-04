from result import Either, is_fail, result_fail, result_ok
from boilerplate import (
    ApplicationErrorID,
    AuthenticationError,
    CoreError,
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    IQueryUseCase,
)
from shared.domain.types.user_id import UserId
from expenses.infrastructure.mappers.expense_mapper import create_unique_entity_id
from expenses.domain.read_models.expense_read_model import ExpenseReadModel
from expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseUsecase(IQueryUseCase[UserId, ExpenseReadModel]):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, aggregate_id: str, user_id: UserId) -> Either[
        ExpenseReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
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
                    "You do not have permission to view this expense",
                )
            )

        return result_ok(result.value)
