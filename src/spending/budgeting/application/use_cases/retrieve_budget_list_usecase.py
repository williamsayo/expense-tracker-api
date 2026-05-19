from typing import Sequence
from boilerplate import CoreError
from result import Either, is_fail, result_ok
from src.shared.domain.types.user_id import UserId
from boilerplate.errors.repository import (
    RepositoryUnexpectedError,
    DataIntegrityError,
)
from src.spending.budgeting.infrastructure.adapters.dto.budget import BudgetReadModel
from src.spending.budgeting.utils.setup_dependencies import BudgetReadDeps
class GetBudgetsUsecase:
    def __init__(self, deps: BudgetReadDeps):
        self.deps = deps

    async def execute(self, user_id: UserId) -> Either[
        Sequence[BudgetReadModel],
        CoreError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Lists all budgets."""
        result = await self.deps.repo.list({"filter": {"user_id": user_id}})

        if is_fail(result):
            return result

        return result_ok(result.value)
