from datetime import date
from typing import TypedDict
from boilerplate import AsyncQueryUseCase, CoreError
from result import Either, is_fail, result_combine, result_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
)


class GetOverviewInput(TypedDict):
    user_id: UserId
    period: date


class GetOverviewUsecase(AsyncQueryUseCase[GetOverviewInput, dict]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: GetOverviewInput) -> Either[
        dict,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves an overview for the dashboard."""
        user_id = str(input["user_id"])
        period = input["period"]

        spending_summary_result = await self.deps.repository.get_spending_summary(
            user_id, period
        )
        recent_expenses_result = await self.deps.repository.get_recent_expenses(user_id)

        combined_result = result_combine(
            (spending_summary_result, recent_expenses_result)
        )

        if is_fail(combined_result):
            return combined_result

        spending_summary, recent_expenses = combined_result.value

        return result_ok({**spending_summary, "recent_expenses": recent_expenses})
