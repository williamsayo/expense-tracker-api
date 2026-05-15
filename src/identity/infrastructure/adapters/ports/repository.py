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
from boilerplate.errors.http import AuthorizationError
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService


class UserRepositoryProtocol(Protocol):
    """Defines the contract for user repository operations."""

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        UserEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def add(
        self, aggregate: UserEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]: ...

    async def username_exists(
        self, username: str, *, email: str
    ) -> Either[bool, RepositoryUnexpectedError]: ...

    async def exists(self, aggregate_id: UniqueEntityId) -> Either[bool, RepositoryUnexpectedError]: ...

    async def first(
        self, options: GetOptions, encryption: EncryptionService, password: str
    ) -> Either[
        UserEntity,
        RepositoryNotFoundError
        | DataIntegrityError
        | RepositoryUnexpectedError
        | AuthorizationError,
    ]: ...
