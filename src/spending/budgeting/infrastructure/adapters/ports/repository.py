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
    BudgetOverviewReadModel,
)


class BudgetRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]: ...

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


class BudgetReadRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UUID | str) -> Either[
        BudgetReadModel,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetReadModel
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

    async def get_budget_overview(self, options: GetAllOptions[AppFilter]) -> Either[
        BudgetOverviewReadModel,
        RepositoryUnexpectedError,
    ]: ...
