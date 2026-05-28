from datetime import date
from typing import Protocol
from uuid import UUID
from boilerplate import (
    CoreError,
    RepositoryNotFoundError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
)
from result import Either
from src.dashboard.domain.read_models.spending_overview_read_model import (
    BudgetReadModel,
    SpendingOverviewReadModel,
    ExpenseReadModel,
)
from src.dashboard.domain.read_models.recent_financials_read_model import (
    RecentFinancialsReadModel,
)
from src.dashboard.domain.read_models.dashboard_overview_read_model import (
    SpendingInsightReadModel,
)
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    DashboardPublicModel,
)


class DashboardRepositoryProtocol(Protocol):

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[SpendingOverviewReadModel, CoreError]: ...

    async def get_overview_by_id(
        self, user_id: str, period: date
    ) -> Either[
        DashboardPublicModel, RepositoryNotFoundError | RepositoryUnexpectedError
    ]: ...

    async def get_spending_insight(
        self, user_id: str
    ) -> Either[list[SpendingInsightReadModel], RepositoryUnexpectedError]: ...

    async def get_recent_financials(
        self, user_id: str
    ) -> Either[
        RecentFinancialsReadModel, RepositoryUnexpectedError | RepositoryNotFoundError
    ]: ...

    async def add(
        self,
        aggregate: SpendingOverviewReadModel | RecentFinancialsReadModel,
        *,
        sort_key: str | None = None,
    ) -> Either[None, CoreError]: ...

    async def remove(
        self, aggregate: SpendingOverviewReadModel, *, sort_key: str | None = None
    ) -> Either[None, CoreError]: ...

    async def exists(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[bool, RepositoryUnexpectedError]: ...

    async def add_Budget(
        self, user_id: str, aggregate: BudgetReadModel
    ) -> Either[None, RepositoryUnexpectedError]: ...

    async def add_expense(
        self, user_id: str, aggregate: ExpenseReadModel
    ) -> Either[None, RepositoryUnexpectedError]: ...
