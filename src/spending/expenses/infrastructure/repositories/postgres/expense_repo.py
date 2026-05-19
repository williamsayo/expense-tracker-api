from typing import Sequence, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, delete
from sqlalchemy.engine import CursorResult
from boilerplate import (
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConflictError,
    ConcurrencyError,
    RepositoryNotFoundError,
    GetAllOptions,
    GetOptions,
    AuthenticationError,
    AuthenticationError,
    AsyncWriteRepository,
    UniqueEntityId,
)
from result import result_fail, result_ok, is_fail, Either, result_combine
from src.shared.domain.types.user_id import UserId
from src.shared.utils.build_query import AppFilter, build_query
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from src.spending.expenses.infrastructure.mappers.expense_mapper import ExpenseMapper
from src.spending.expenses.infrastructure.repositories.schema import Expense


class ExpenseRepository(AsyncWriteRepository[ExpenseEntity, UniqueEntityId]):
    """Repository implementation for expense data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[ExpenseEntity], RepositoryUnexpectedError | DataIntegrityError
    ]:
        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required for listing expenses"),
                    "User ID filter is required for listing expenses",
                )
            )

        statement = build_query(Expense, options)

        result = await self.db.scalars(statement)
        persistence_output = result.all()

        result = tuple(
            ExpenseMapper.to_domain(persistence) for persistence in persistence_output
        )
        entity_result = result_combine(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        query = await self.db.scalars(
            select(Expense).where(Expense.id == aggregate_id.value)
        )
        result = query.one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        entity_result = ExpenseMapper.to_domain(result)

        if is_fail(entity_result):
            return result_fail(DataIntegrityError(Exception(entity_result.value)))

        return result_ok(entity_result.value)

    async def add(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:
        try:
            persistence = ExpenseMapper.to_persistence(aggregate)
            exists = await self.exists(aggregate.id)
            if exists:
                await self.db.merge(persistence)
            else:
                self.db.add(persistence)

            await self.db.commit()

            return result_ok()
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

    async def exists(
        self, aggregate_id: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]:
        query = await self.db.scalars(
            select(exists().where(Expense.id == aggregate_id.value))
        )
        return result_ok(cast(bool, query.one_or_none()))

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID is required in filter for first method")
                )
            )

        result = await self.db.scalars(build_query(Expense, options))

        persistence_output = result.first()

        if not persistence_output:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        result = ExpenseMapper.to_domain(persistence_output)

        if is_fail(result):
            return result_fail(DataIntegrityError(Exception(result.value)))

        return result_ok(result.value)

    async def remove(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError]:
        # TODO: optimize this by removing the select query and directly executing the delete query, but we need to ensure that the expense belongs to the user before deleting it
        # persistence = ExpenseMapper.to_persistence(aggregate)
        try:
            statement = delete(Expense).where(Expense.id == aggregate.id.value)
            await self.db.execute(statement)
            await self.db.commit()
        except Exception as error:
            print("Error removing expense:", error)
            return result_fail(RepositoryUnexpectedError(error))

        return result_ok()

    async def remove_all(
        self, category: str, user_id: UserId
    ) -> Either[int, RepositoryUnexpectedError | AuthenticationError]:
        statement = delete(Expense).where(
            Expense.category == category, Expense.user_id == user_id
        )
        try:
            result = await self.db.execute(statement)
            await self.db.commit()
            cursor_result = cast(CursorResult, result)
        except Exception as error:
            return result_fail(RepositoryUnexpectedError(error))

        return result_ok(cursor_result.rowcount)
