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
from budgeting.domain.entities.budget_entity import BudgetEntity
from identity.infrastructure.services.encryption.base import EncryptionService


class BudgetRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(self, aggregate_id: UniqueEntityId) -> bool: ...

    async def list(
        self, options: GetAllOptions
    ) -> Either[
        Sequence[BudgetEntity], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions) -> Either[
        BudgetEntity,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...

    async def remove(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...
