from typing import Sequence
from result import Either, is_fail, result_ok
from shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    IQueryUseCase,
)
from expenses.domain.read_models.expense_read_model import ExpenseReadModel
from expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseListUsecase(IQueryUseCase[UserId, ExpenseReadModel]):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, user_id: UserId) -> Either[
        Sequence[ExpenseReadModel],
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        result = await self.deps.repo.list(
            {"filter": {"user_id": user_id}, "limit": 20}
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
