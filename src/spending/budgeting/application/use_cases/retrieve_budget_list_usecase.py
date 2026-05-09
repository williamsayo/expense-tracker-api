from typing import Protocol, Sequence
from boilerplate import CoreError
from result import Either, is_fail, result_ok, result_fail
from shared.domain.types.user_id import UserId
from boilerplate.errors.repository import (
    RepositoryUnexpectedError,
    DataIntegrityError,
)
from spending.budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel
from spending.budgeting.utils.setup_dependencies import BudgetReadDeps


class GetBudgetsUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, user_id: UserId) -> Either[
        Sequence[BudgetSummaryReadModel],
        CoreError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Lists all budgets."""
        result = await self.deps.repo.list({"filter": {"user_id": user_id}})

        if is_fail(result):
            return result

        return result_ok(result.value)
