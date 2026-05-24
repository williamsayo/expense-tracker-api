from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    AsyncCommandUseCase,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok, result_combine
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    BudgetReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import BudgetCreatedEventPayload
from ..services.budget_maintaier import BudgetMaintainer


class UpdateBudgetProjectionInput(TypedDict):
    user_id: str
    budget: BudgetCreatedEventPayload


class UpdateBudgetProjectionUsecase(AsyncCommandUseCase[UpdateBudgetProjectionInput]):

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def execute(self, input: UpdateBudgetProjectionInput) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        user_id, budget = input["user_id"], input["budget"]

        data = budget.data

        budget_maintainer_service = BudgetMaintainer()

        total_amount = budget_maintainer_service.calculate_budget_total(
            data.allocations
        )

        budget_projection = BudgetReadModel(
            id=data.budget_id,
            name=data.name,
            total_amount=total_amount,
            start_date=data.start_date.isoformat(),
            end_date=data.end_date.isoformat(),
        )

        budget_projection_result = await self.deps.repository.add_Budget(
            user_id, budget_projection
        )

        overview_result = await self.deps.repository.get_by_id(user_id)

        combined_result = result_combine((budget_projection_result, overview_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        _, overview = combined_result.value

        total_budgeted = budget_maintainer_service.calculate_total_budgeted(
            overview.total_budgeted, total_amount
        )

        active_budget = budget_maintainer_service.determine_active_budget(
            overview.active_budget, budget_projection
        )

        dashboard_overview = overview.model_copy(
            update={
                "total_budgeted": total_budgeted,
                "active_budget": active_budget,
            }
        )

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().isoformat()}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)
