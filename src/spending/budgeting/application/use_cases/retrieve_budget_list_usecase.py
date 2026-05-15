from typing import Sequence
from uuid import UUID
from boilerplate import CoreError
from result import Either, is_fail, result_ok
from boilerplate.errors.repository import (
    RepositoryUnexpectedError,
    DataIntegrityError,
)
from src.spending.budgeting.domain.read_models.budget_summary import (
    BudgetSummaryReadModel,
)
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps


class GetBudgetsUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, auth_id: UUID) -> Either[
        Sequence[BudgetSummaryReadModel],
        CoreError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Lists all budgets."""
        result = await self.deps.repo.list({"filter": {"auth_id": auth_id}})

        if is_fail(result):
            return result

        return result_ok(result.value)
