from datetime import date
from typing import TypedDict
from boilerplate import AsyncQueryUseCase, CoreError
from result import Either, is_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
)
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    DashboardPublicModel,
)

class GetOverviewInput(TypedDict):
    user_id: UserId
    period: date


class GetOverviewUsecase(AsyncQueryUseCase[GetOverviewInput, DashboardPublicModel]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: GetOverviewInput) -> Either[
        DashboardPublicModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves an overview for the dashboard."""
        user_id = str(input["user_id"])
        period = input["period"]

        result = await self.deps.repository.get_overview_by_id(user_id, period)

        if is_fail(result):
            return result

        return result_ok(result.value)
