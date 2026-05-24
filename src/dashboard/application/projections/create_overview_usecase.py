from datetime import date
from typing import Any, TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncCommandUseCase,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.infrastructure.adapters.dto.dashboard import DashboardReadModel

class CreateOverviewInput(TypedDict):
    user_id: str
    overview_data: dict[str, Any]


class CreateOverviewUsecase(AsyncCommandUseCase[CreateOverviewInput]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: CreateOverviewInput) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        user_id, data = input["user_id"], input["overview_data"]

        dashboard_overview = DashboardReadModel(user_id=user_id, **data)

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(result.value)
