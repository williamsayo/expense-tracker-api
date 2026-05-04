from typing import Protocol, Sequence
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
from shared.domain.types.user_id import UserId
from expenses.domain.entities.expense_entity import ExpenseEntity
from expenses.domain.read_models.expense_overview_read_model import (
    ExpenseOverviewReadModel,
)
from expenses.domain.read_models.expense_read_model import ExpenseReadModel


class ExpenseRepositoryProtocol(Protocol):
    """Defines the contract for expense repository operations."""

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def add(
        self, aggregate: ExpenseEntity
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
    ) -> Either[None, RepositoryUnexpectedError | AuthenticationError]: ...

    async def remove_all(
        self, category: str, user_id: UserId
    ) -> Either[int, RepositoryUnexpectedError | AuthenticationError]: ...


class ExpenseReadRepositoryProtocol(Protocol):
    """Defines the contract for expense read repository operations."""

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def list(
        self, options: GetAllOptions
    ) -> Either[
        Sequence[ExpenseReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]: ...

    async def first(self, options: GetOptions) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]: ...

    async def get_expense_overview(self, options: GetAllOptions) -> Either[
        ExpenseOverviewReadModel,
        RepositoryUnexpectedError | DataIntegrityError,
    ]: ...
