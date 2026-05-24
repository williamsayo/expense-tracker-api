from typing import Protocol
from uuid import UUID
from boilerplate import (
    CoreError,
    RepositoryUnexpectedError,
)
from result import Either
from src.dashboard.infrastructure.adapters.dto.dashboard import (
    DashboardReadModel,
)


class DashboardRepositoryProtocol(Protocol):

    async def get_by_id(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[DashboardReadModel, CoreError]: ...

    async def add(self, aggregate: DashboardReadModel) -> Either[None, CoreError]: ...

    async def remove(
        self, aggregate: DashboardReadModel
    ) -> Either[None, CoreError]: ...

    async def exists(
        self, aggregate_id: str | UUID, *, sort_key: str | None = None
    ) -> Either[bool, RepositoryUnexpectedError]: ...
