from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from boilerplate import (
    AsyncReadRepository,
    DataIntegrityError,
    RepositoryUnexpectedError,
    RepositoryNotFoundError,
    GetAllOptions,
    GetOptions,
    ConcurrencyError,
    ConflictError,
)
from result import result_fail, result_ok, Either
from src.shared.utils.build_query import AppFilter, build_query
from src.spending.expenses.infrastructure.adapters.dto.expense import (
    ExpenseReadModel,
    ExpenseOverviewReadModel,
)
from src.spending.expenses.infrastructure.repositories.schema import Expense


class ExpenseReadRepository(AsyncReadRepository[ExpenseReadModel]):
    """Repository implementation for expense data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, aggregate_id: str | UUID) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        query = await self.db.execute(
            select(Expense.__table__).where(Expense.id == aggregate_id)
        )
        result = query.mappings().one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        read_model = ExpenseReadModel(**result)

        return result_ok(read_model)

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[ExpenseReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]:

        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required for listing expenses"),
                    "User ID filter is required for listing expenses",
                )
            )

        statement = build_query(Expense.__table__, options)

        result = await self.db.execute(statement)
        persistence_output = result.mappings().all()

        read_model = [
            ExpenseReadModel(**persistence) for persistence in persistence_output
        ]

        return result_ok(read_model)

    async def get_expense_overview(self, options: GetAllOptions[AppFilter]) -> Either[
        ExpenseOverviewReadModel,
        RepositoryUnexpectedError | DataIntegrityError,
    ]:
        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required for overview"),
                    "User ID filter is required for overview",
                )
            )

        statement = build_query(Expense.__table__, options)

        recent_expenses = statement.order_by(Expense.date.desc()).limit(
            options.get("limit", 5)
        )

        total_spent = select(func.sum(Expense.amount).label("total_spent")).where(
            Expense.user_id == user_id
        )

        highest_spent = statement.order_by(Expense.amount.desc())

        result = await self.db.execute(recent_expenses)
        persistence_output = result.mappings().all()

        highest_spent_result = await self.db.execute(highest_spent)
        highest_spent_output = highest_spent_result.mappings().first()

        total_spent_result = await self.db.scalars(total_spent)
        total_spent_output = total_spent_result.first()

        read_model = [
            ExpenseReadModel(**persistence) for persistence in persistence_output
        ]

        if highest_spent_output is not None:
            highest_spent_output = ExpenseReadModel(**highest_spent_output)

        overview_read_model = ExpenseOverviewReadModel(
            user_id=user_id,
            recent_expenses=read_model,
            total_spent=total_spent_output if total_spent_output else 0,
            highest_expense=highest_spent_output,
        )

        return result_ok(overview_read_model)

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID is required in filter for first method")
                )
            )

        statement = build_query(Expense.__table__, options)

        result = await self.db.execute(statement)

        persistence_output = result.mappings().first()

        if not persistence_output:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        read_model = ExpenseReadModel(**persistence_output)

        return result_ok(read_model)

    async def add(self, aggregate: ExpenseReadModel) -> Either[
        None,
        RepositoryUnexpectedError | ConcurrencyError | ConflictError,
    ]: ...
    async def exists(
        self, aggregateId: str | UUID
    ) -> Either[bool, RepositoryUnexpectedError]: ...

    async def remove(self, aggregate: ExpenseReadModel) -> Either[
        None,
        RepositoryUnexpectedError | ConcurrencyError | ConflictError,
    ]: ...

    async def commit(self) -> Either[None, RepositoryUnexpectedError]:
        try:
            await self.db.commit()
            return result_ok()
        except Exception as error:
            await self.db.rollback()
            return result_fail(RepositoryUnexpectedError(error))
