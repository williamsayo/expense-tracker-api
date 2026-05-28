import asyncio
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
from src.dashboard.domain.read_models.recent_financials_read_model import (
    RecentFinancialsReadModel,
)
from src.dashboard.domain.read_models.spending_overview_read_model import (
    SpendingOverviewReadModel,
)


class CreateOverviewInput(TypedDict):
    user_id: str
    spending_data: dict[str, Any]
    recents_data: dict[str, Any]


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

        user_id, spending_data, recents_data = (
            input["user_id"],
            input["spending_data"],
            input["recents_data"],
        )

        dashboard_overview = SpendingOverviewReadModel(
            user_id=user_id,
            active_budget=spending_data["active_budget"],
            upcoming_budget=spending_data["upcoming_budget"],
            total_spent=spending_data["total_spent"],
            total_budgeted=spending_data["total_budgeted"],
            top_categories=spending_data["top_categories"],
            top_expense=spending_data["top_expense"],
            period=spending_data["period"],
        )
        
        recents_read_model = RecentFinancialsReadModel(
            user_id=user_id,
            recent_expenses=recents_data["recent_expenses"],
            recent_budgets=recents_data["recent_budgets"],
        )

        result = await asyncio.gather(
            self.deps.repository.add(
                dashboard_overview,
                sort_key=f"overview#{date.today().strftime('%Y-%m')}",
            ),
            self.deps.repository.add(
                recents_read_model,
                sort_key="recents",
            ),
        )

        combined_result = result_combine(result)

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        return result_ok(None)
