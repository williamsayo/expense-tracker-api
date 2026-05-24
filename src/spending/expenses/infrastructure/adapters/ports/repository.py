from typing import Protocol, Sequence
from uuid import UUID
from result import Either
from boilerplate import (
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
    UniqueEntityId,
    AuthenticationError,
    GetAllOptions,
    GetOptions,
)
from src.shared.domain.types.user_id import UserId
from src.shared.utils.build_query import AppFilter
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.adapters.dto.expense import ExpenseReadModel


class ExpenseRepositoryProtocol(Protocol):
    """Defines the contract for expense repository operations."""

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def add(
        self, aggregate: ExpenseEntity, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]: ...

    async def exists(self, aggregate_id: UniqueEntityId) -> Either[bool, RepositoryUnexpectedError]: ...

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[ExpenseEntity], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def remove(
        self, aggregate: ExpenseEntity, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | AuthenticationError]: ...

    async def remove_all(
        self, category: str, user_id: UserId, *, auto_commit: bool = True
    ) -> Either[int, RepositoryUnexpectedError | AuthenticationError]: ...


class ExpenseReadRepositoryProtocol(Protocol):
    """Defines the contract for expense read repository operations."""

    async def get_by_id(self, aggregate_id: str | UUID) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[ExpenseReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...