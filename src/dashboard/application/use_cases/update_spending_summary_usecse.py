from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncCommandUseCase,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.domain.read_models.overview_read_model import (
    BudgetReadModel,
    DashboardOverviewReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import BudgetCreatedEventPayload


class UpdateSpendingSummaryInput(TypedDict):
    user_id: str
    budget: BudgetCreatedEventPayload


class UpdateSpendingSummaryUsecase(AsyncCommandUseCase[UpdateSpendingSummaryInput]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: UpdateSpendingSummaryInput) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        user_id, budget = input["user_id"], input["budget"]

        data = budget.data

        overview_result = await self.deps.repository.get_by_id(user_id)

        if is_fail(overview_result):
            return result_fail(overview_result.value)

        overview = overview_result.value

        total_budget = sum(
            allocation["budget_amount"] for allocation in data.allocations
        )

        total_budgeted = overview.total_budgeted + total_budget

        active_budget = overview.active_budget

        if data.start_date <= date.today() <= data.end_date:
            active_budget = BudgetReadModel(
                name=data.name,
                total_amount=total_budget,
                spent_amount=0,
                start_date=data.start_date.isoformat(),
                end_date=data.end_date.isoformat(),
            )

        dashboard_overview = DashboardOverviewReadModel(
            user_id=user_id,
            total_spent=overview.total_spent,
            total_budgeted=total_budgeted,
            top_expense=overview.top_expense,
            top_category=overview.top_category,
            recent_expenses=overview.recent_expenses,
            active_budget=active_budget,
        )

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)
