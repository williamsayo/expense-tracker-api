from boilerplate import CoreError
from result import Either, is_fail, result_ok
from src.shared.domain.types.user_id import UserId
from boilerplate import (
    RepositoryUnexpectedError,
    DataIntegrityError,
    RepositoryNotFoundError,
)
from src.spending.expenses.domain.read_models.expense_overview_read_model import (
    ExpenseOverviewReadModel,
)
from src.spending.expenses.utils.setup_dependencies import ExpenseReadDeps


class GetExpenseOverviewUsecase:
    def __init__(self, deps: ExpenseReadDeps):
        self.deps = deps

    async def execute(self, auth_id: UserId, limit: int) -> Either[
        ExpenseOverviewReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:
        """Retrieves a budget by its ID."""
        result = await self.deps.repo.get_expense_overview(
            {"filter": {"auth_id": auth_id}, "limit": limit}
        )

        if is_fail(result):
            return result

        return result_ok(result.value)
