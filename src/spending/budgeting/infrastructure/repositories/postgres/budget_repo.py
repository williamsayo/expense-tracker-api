from sqlalchemy import select, exists, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence, cast
from boilerplate import (
    AsyncReadRepository,
    AsyncWriteRepository,
    ConcurrencyError,
    ConflictError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    WriteRepository,
    ReadRepository,
    UniqueEntityId,
    GetAllOptions,
    GetOptions,
)

from result import Either, result_combine, result_ok, result_fail, is_fail
from spending.budgeting.domain.entities.budget_entity import BudgetEntity
from spending.budgeting.infrastructure.repositories.schema import Budget
from spending.budgeting.infrastructure.mappers.budget_mapper import BudgetMapper


class BudgetRepository(AsyncWriteRepository[BudgetEntity, UniqueEntityId]):
    """Repository implementation for budget data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        """Adds a new budget entity to the database."""
        persistence = BudgetMapper.to_persistence(aggregate)
        exists = await self.exists(aggregate.id)

        if is_fail(exists):
            return result_fail(
                RepositoryUnexpectedError(
                    Exception(exists.value), "Failed to check if budget exists"
                )
            )

        if exists:
            await self.db.merge(persistence)
        else:
            self.db.add(persistence)

        await self.db.commit()

        return result_ok()

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]:
        statement = select(exists().where(Budget.id == aggregate_id.value))
        result = await self.db.scalar(statement)
        return result_ok(cast(bool, result))

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Retrieves a budget entity by its unique identifier."""

        statement = (
            select(Budget)
            .where(Budget.id == aggregate_id.value)
            .options(selectinload(Budget.allocations))
        )
        result = (await self.db.scalars(statement)).one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetMapper.to_domain(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def list(
        self, options: GetAllOptions
    ) -> Either[Sequence[BudgetEntity], RepositoryUnexpectedError | DataIntegrityError]:
        statement = select(Budget).options(selectinload(Budget.allocations))

        if filter := options.get("filter"):
            if "start_date" in filter and "end_date" in filter:
                new_start = filter.pop("start_date")
                new_end = filter.pop("end_date")

                statement = statement.where(
                    and_(
                        Budget.start_date <= new_end,  # existing starts before new ends
                        Budget.end_date >= new_start,  # existing ends after new starts
                    )
                )

            statement = statement.filter_by(**filter)

        result = await self.db.scalars(statement)
        persistence_output = result.all()

        result = tuple(
            BudgetMapper.to_domain(persistence) for persistence in persistence_output
        )

        entity_result = result_combine(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def first(self, options: GetOptions) -> Either[
        BudgetEntity,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        statement = select(Budget).options(selectinload(Budget.allocations))

        if filter := options.get("filter"):
            # Handle date range overlap
            if "start_date" in filter and "end_date" in filter:
                new_start = filter.pop("start_date")
                new_end = filter.pop("end_date")

                statement = statement.where(
                    and_(
                        Budget.start_date <= new_end,  # existing starts before new ends
                        Budget.end_date >= new_start,  # existing ends after new starts
                    )
                )

            statement = statement.filter_by(**filter)

        persistence_output = await self.db.scalar(statement)

        if persistence_output is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetMapper.to_domain(persistence_output)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def remove(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...
