from typing import Protocol
from boilerplate import (
    UniqueEntityId,
    CoreError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    DataIntegrityError,
)
from result import Either
from domain.entities.example import ExampleEntity
from src.dashboard.domain.read_models.overview_read_model import (
    DashboardOverviewReadModel,
)


class DashboardRepositoryProtocol(Protocol):
    async def get_by_id(
        self, id: UniqueEntityId
    ) -> Either[DashboardOverviewReadModel, None]: ...

    async def add(self, entity: ExampleEntity) -> Either[None, Exception]: ...

    async def remove(self, entity: ExampleEntity) -> Either[None, Exception]: ...

    async def exists(self, id: UniqueEntityId) -> Either[bool, Exception]: ...
