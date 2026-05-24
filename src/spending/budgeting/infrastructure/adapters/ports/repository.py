from datetime import date
from uuid import UUID
from typing import Protocol, Sequence
from result import Either
from boilerplate import (
    UniqueEntityId,
    RepositoryNotFoundError,
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConcurrencyError,
    ConflictError,
    GetAllOptions,
    GetOptions,
)
from src.shared.utils.build_query import AppFilter
from src.spending.budgeting.domain.entities.budget_entity import BudgetEntity
from src.spending.budgeting.infrastructure.adapters.dto.budget import (
    BudgetReadModel,
)


class BudgetFilter(AppFilter):
    start_date: date
    end_date: date


class BudgetRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetEntity, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]: ...

    async def list(
        self, options: GetAllOptions[BudgetFilter]
    ) -> Either[
        Sequence[BudgetEntity], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions[BudgetFilter]) -> Either[
        BudgetEntity,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...

    async def remove(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions[BudgetFilter]
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...


class BudgetReadRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UUID | str) -> Either[
        BudgetReadModel,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetReadModel, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(
        self, aggregate_id: UUID | str
    ) -> Either[bool, RepositoryUnexpectedError]: ...

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[BudgetReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        BudgetReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...

    async def remove(
        self, aggregate: BudgetReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...