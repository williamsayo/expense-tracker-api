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
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    DashboardReadModel,
)


class GetOverviewInput(TypedDict):
    user_id: UserId
    period: date


class GetOverviewUsecase(AsyncQueryUseCase[GetOverviewInput, DashboardReadModel]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: GetOverviewInput) -> Either[
        DashboardReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves an overview for the dashboard."""
        user_id = str(input["user_id"])
        period = input["period"]

        overview_result = await self.deps.repository.get_by_id(user_id,sort_key=f"overview#{period.strftime('%Y-%m')}")

        if is_fail(overview_result):
            return overview_result

        return result_ok(overview_result.value)
