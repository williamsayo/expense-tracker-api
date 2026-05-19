from typing import Sequence, TypedDict
from uuid import UUID
from result import Either, is_fail, result_ok
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncQueryUseCase,
)
from src.spending.expenses.infrastructure.adapters.dto.expense import ExpenseReadModel
from src.spending.expenses.utils.setup_dependencies import ExpenseReadDeps
from src.shared.application.dtos.url_params import UrlParams


class GetExpenseListInput(TypedDict):
    user_id: UUID
    queryParams: UrlParams


class GetExpenseListUsecase(
    AsyncQueryUseCase[GetExpenseListInput, Sequence[ExpenseReadModel]]
):
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, input: GetExpenseListInput) -> Either[
        Sequence[ExpenseReadModel],
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        result = await self.deps.repo.list(
            {
                "filter": {"user_id": input["user_id"]},
                "limit": input["queryParams"].page_size,
            }
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
