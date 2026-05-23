from datetime import date
from typing import Any, TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncCommandUseCase,
    CoreError,
)
from result import Either, is_fail, result_combine, result_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.domain.read_models.overview_read_model import (
    DashboardOverviewReadModel,
)
from src.dashboard.infrastructure.adapters.dto.dashboard import DashboardWriteModel


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

        dashboard_overview = DashboardOverviewReadModel(user_id=user_id, **data)

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        recent_expenses_result = await self.deps.repository.add_recent_expense(
            user_id, []
        )

        combined_result = result_combine((result, recent_expenses_result))

        if is_fail(combined_result):
            return combined_result

        return result_ok(None)
