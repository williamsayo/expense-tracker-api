from typing import Protocol, Sequence
from boilerplate import GetAllOptions, GetOptions
from result import Either
from boilerplate.domain.unique_entity_id import UniqueEntityId
from boilerplate.errors.repository import (
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
)
from identity.domain.entities.user_entity import UserEntity
from identity.infrastructure.services.encryption.base import EncryptionService


class UserRepositoryProtocol(Protocol):
    """Defines the contract for user repository operations."""

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def add(
        self, aggregate: UserEntity
    ) -> Either[
        UserEntity, RepositoryUnexpectedError | ConflictError | ConcurrencyError
    ]: ...

    async def username_exists(
        self, username: str, aggregateId: UniqueEntityId, *, email: str
    ) -> bool: ...

    async def exists(self, aggregateId: UniqueEntityId) -> bool: ...

    async def first(
        self, options: GetOptions, encryption: EncryptionService, password: str
    ) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...
