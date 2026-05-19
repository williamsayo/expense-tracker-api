from boilerplate import CoreError
from result import Either, is_fail, result_ok
from src.shared.domain.types.user_id import UserId
from boilerplate.errors.repository import RepositoryUnexpectedError
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps
from src.spending.budgeting.infrastructure.adapters.dto.budget import (
    BudgetOverviewReadModel,
)


class GetBudgetOverviewUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, user_id: UserId, limit: int) -> Either[
        BudgetOverviewReadModel,
        CoreError | RepositoryUnexpectedError,
    ]:
        """Retrieves the budget overview for a user."""
        result = await self.deps.repo.get_budget_overview(
            {
                "filter": {"user_id": user_id},
                "limit": limit,
                "select": ["id", "currency", "name", "start_date", "end_date"],
            }
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
