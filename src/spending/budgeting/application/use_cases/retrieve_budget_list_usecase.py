from typing import Sequence, TypedDict
from uuid import UUID
from boilerplate import CoreError
from result import Either, is_fail, result_ok
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    AsyncQueryUseCase,
)
from src.spending.budgeting.infrastructure.adapters.dto.budget import BudgetReadModel
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps
from src.shared.application.dtos.url_params import UrlParams


class GetBudgetListInput(TypedDict):
    user_id: UUID
    query_params: UrlParams


class GetBudgetsUsecase(
    AsyncQueryUseCase[GetBudgetListInput, Sequence[BudgetReadModel]]
):
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, input: GetBudgetListInput) -> Either[
        Sequence[BudgetReadModel],
        CoreError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Lists all budgets."""

        query_params = input["query_params"]

        result = await self.deps.repo.list(
            {
                "filter": {"user_id": input["user_id"]},
                "limit": query_params.page_size,
                "offset": query_params.page,
                "q": query_params.q,
            }
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
