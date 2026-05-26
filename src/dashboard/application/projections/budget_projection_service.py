from datetime import date
from typing import TypedDict
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
    CoreError,
)
from result import Either, is_fail, result_fail, result_ok, result_combine
from src.dashboard.utils.setup_dependencies import OverviewDeps
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    BudgetReadModel,
)
from src.dashboard.infrastructure.adapters.dto.event import BudgetCreatedEventPayload
from ..services.budget_overview_applier_service import BudgetProjectionApplierService

class UpdateBudgetProjectionInput(TypedDict):
    user_id: str
    budget: BudgetCreatedEventPayload


class BudgetProjectionService:

    def __init__(self, deps: OverviewDeps):
        self.deps = deps

    async def apply_budget_projection(
        self, user_id: str, budget_projection: BudgetReadModel
    ) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        budget_projection_result = await self.deps.repository.add_Budget(
            user_id, budget_projection
        )

        if is_fail(budget_projection_result):
            return result_fail(budget_projection_result.value)

        return result_ok(None)

    async def update_overview_on_budget_created(
        self, input: UpdateBudgetProjectionInput
    ) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        user_id, budget = input["user_id"], input["budget"]

        data = budget.data

        budget_projection_service = BudgetProjectionApplierService()

        total_amount = budget_projection_service.compute_allocations_total(
            data.allocations
        )

        budget_projection = BudgetReadModel(
            id=data.budget_id,
            name=data.name,
            total_amount=total_amount,
            start_date=data.start_date.isoformat(),
            end_date=data.end_date.isoformat(),
        )

        budget_projection_result = await self.apply_budget_projection(
            user_id, budget_projection
        )

        overview_result = await self.deps.repository.get_by_id(user_id)

        combined_result = result_combine((budget_projection_result, overview_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        _, overview = combined_result.value

        total_budgeted = budget_projection_service.increment_total_budgeted(
            overview.total_budgeted, total_amount
        )

        active_budget = budget_projection_service.resolve_active_budget(
            overview.active_budget, budget_projection
        )

        recent_budgets = budget_projection_service.update_recent_budgets(
            overview.recent_budgets, budget_projection
        )

        upcoming_budget = budget_projection_service.resolve_upcoming_budget(
            overview.upcoming_budget, budget_projection
        )

        dashboard_overview = overview.model_copy(
            update={
                "total_budgeted": total_budgeted,
                "active_budget": active_budget,
                "recent_budgets": recent_budgets,
                "upcoming_budget": upcoming_budget,
            }
        )

        result = await self.deps.repository.add(
            dashboard_overview, sort_key=f"overview#{date.today().strftime('%Y-%m')}"
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(None)

    async def update_overview_on_budget_updated(
        self, input: UpdateBudgetProjectionInput
    ) -> Either[
        None,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        # For simplicity, we'll just re-use the same logic as creation for now.
        # In a real implementation, we would want to compute the difference in total budgeted amount and adjust the overview accordingly, rather than re-computing from scratch.
        return await self.update_overview_on_budget_created(input)
