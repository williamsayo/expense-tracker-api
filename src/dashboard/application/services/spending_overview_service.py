from datetime import date
from boilerplate import (
    CoreError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
)
from result import is_fail, result_fail, result_ok, Either
from src.dashboard.infrastructure.adapters.ports.repository import (
    DashboardRepositoryProtocol,
)
from src.dashboard.domain.read_models.spending_overview_read_model import (
    SpendingOverviewReadModel,
)


class CreateSpendingOverviewService:
    def __init__(self, repository: DashboardRepositoryProtocol):
        self.repository = repository

    async def execute(self, user_id: str) -> Either[
        SpendingOverviewReadModel,
        CoreError
        | RepositoryNotFoundError
        | RepositoryUnexpectedError
        | DataIntegrityError,
    ]:

        current_period = date.today().strftime("%Y-%m")

        spending_overview = SpendingOverviewReadModel(
            user_id=user_id,
            active_budget=None,
            upcoming_budget=None,
            total_spent=0,
            total_budgeted=0,
            top_categories=[],
            top_expense=None,
            period=current_period,
        )

        result = await self.repository.add(
            spending_overview,
            sort_key=f"overview#{current_period}",
        )

        if is_fail(result):
            return result_fail(result.value)

        return result_ok(spending_overview)
