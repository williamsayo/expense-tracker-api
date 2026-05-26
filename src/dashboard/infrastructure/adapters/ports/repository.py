from typing import Protocol
from uuid import UUID
from boilerplate import (
    CoreError,
    RepositoryUnexpectedError,
)
from result import Either
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    BudgetReadModel,
    DashboardReadModel,
    ExpenseReadModel,
)


class DashboardRepositoryProtocol(Protocol):

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[DashboardReadModel, CoreError]: ...

    async def add(
        self, aggregate: DashboardReadModel, *, sort_key: str | None = None
    ) -> Either[None, CoreError]: ...

    async def remove(
        self, aggregate: DashboardReadModel, *, sort_key: str | None = None
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