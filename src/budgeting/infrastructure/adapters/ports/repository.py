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
from budgeting.domain.entities.budget_entity import BudgetEntity
from budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel
from budgeting.domain.read_models.budget_overview import BudgetOverviewReadModel

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


class BudgetReadRepositoryProtocol(Protocol):
    """Defines the contract for budgeting repository operations."""

    async def get_by_id(self, aggregate_id: UUID | str) -> Either[
        BudgetSummaryReadModel,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]: ...

    async def add(
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(self, aggregate_id: UUID | str) -> bool: ...

    async def list(
        self, options: GetAllOptions
    ) -> Either[
        Sequence[BudgetSummaryReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions) -> Either[
        BudgetSummaryReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]: ...

    async def remove(
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def get_budget_overview(self, options: GetAllOptions[str]) -> Either[
        BudgetOverviewReadModel,
        RepositoryUnexpectedError,
    ]: ...
