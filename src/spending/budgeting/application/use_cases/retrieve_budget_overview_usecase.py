from uuid import UUID
from boilerplate import CoreError
from result import Either, is_fail, result_ok
from boilerplate.errors.repository import RepositoryUnexpectedError
from src.spending.budgeting.domain.read_models.budget_overview import (
    BudgetOverviewReadModel,
)
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps


class GetBudgetOverviewUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, auth_id: UUID, limit: int) -> Either[
        BudgetOverviewReadModel,
        CoreError | RepositoryUnexpectedError,
    ]:
        """Retrieves the budget overview for a user."""
        result = await self.deps.repo.get_budget_overview(
            {"filter": {"auth_id": auth_id}, "limit": limit}
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
