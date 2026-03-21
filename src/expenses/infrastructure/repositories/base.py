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
from expenses.domain.entities.expense_entity import ExpenseEntity
from shared.domain.types.user_id import UserId


class ExpenseRepositoryProtocol(Protocol):
    """Defines the contract for expense repository operations."""

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def add(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]: ...

    async def add_all(
        self, aggregates: Sequence[ExpenseEntity]
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]: ...

    async def exists(self, aggregateId: UniqueEntityId) -> bool: ...

    async def list(
        self, options: GetAllOptions
    ) -> Either[
        Sequence[ExpenseEntity], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def remove(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError]: ...

    async def remove_all(
        self, category: str, user_id: UserId
    ) -> Either[int, RepositoryUnexpectedError]: ...
