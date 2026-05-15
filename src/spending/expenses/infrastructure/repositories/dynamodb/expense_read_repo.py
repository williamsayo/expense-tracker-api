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
    ReadRepository,
    UniqueEntityId,
    ConcurrencyError,
    ConflictError,
)
from result import result_fail, result_ok, Either
from src.spending.expenses.domain.read_models.expense_overview_read_model import (
    ExpenseOverviewReadModel,
)
from src.spending.expenses.domain.read_models.expense_read_model import ExpenseReadModel
from src.spending.expenses.infrastructure.repositories.schema import Expense


class ExpenseReadRepository(AsyncReadRepository[ExpenseReadModel]):
    """Repository implementation for expense data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, aggregate_id: str | UUID) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        query = await self.db.scalars(select(Expense).where(Expense.id == aggregate_id))
        result = query.one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        read_model = ExpenseReadModel(
            {
                "id": result.id,
                "name": result.name,
                "user_id": result.user_id,
                "category": result.category,
                "amount": result.amount,
                "currency": result.currency,
                "note": result.note,
                "date": result.date,
            }
        )

        return result_ok(read_model)

    async def list(
        self, options: GetAllOptions[str]
    ) -> Either[
        Sequence[ExpenseReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]:
        statement = select(Expense)
        if filter := options.get("filter"):
            statement = statement.filter_by(**filter)

        if sort := options.get("sort"):
            statement = statement.order_by(
                *[
                    (
                        getattr(Expense, col).desc()
                        if direction == "desc"
                        else getattr(Expense, col).asc()
                    )
                    for col, direction in sort.items()
                ]
            )

        if limit := options.get("limit"):
            statement = statement.limit(limit)

        result = await self.db.scalars(statement)
        persistence_output = result.all()

        read_model = tuple(
            ExpenseReadModel(
                {
                    "id": persistence.id,
                    "name": persistence.name,
                    "user_id": persistence.user_id,
                    "category": persistence.category,
                    "amount": persistence.amount,
                    "currency": persistence.currency,
                    "note": persistence.note,
                    "date": persistence.date,
                }
            )
            for persistence in persistence_output
        )

        return result_ok(read_model)

    async def get_expense_overview(self, options: GetAllOptions[str]) -> Either[
        ExpenseOverviewReadModel,
        RepositoryUnexpectedError | DataIntegrityError,
    ]:
        statement = select(Expense)

        user_id = options.get("filter", {}).get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required for overview"),
                    "User ID filter is required for overview",
                )
            )

        if filter := options.get("filter"):
            statement = statement.filter_by(**filter)

        recent_expenses = statement.order_by(Expense.date.desc()).limit(
            options.get("limit", 5)
        )

        total_spent = select(func.sum(Expense.amount).label("total_spent")).where(
            Expense.user_id == user_id
        )

        highest_spent = statement.order_by(Expense.amount.desc())

        result = await self.db.scalars(recent_expenses)
        persistence_output = result.all()

        highest_spent_result = await self.db.scalars(highest_spent)
        highest_spent_output = highest_spent_result.first()

        total_spent_result = await self.db.scalars(total_spent)
        total_spent_output = total_spent_result.first()

        read_model = [
            ExpenseReadModel(
                {
                    "id": persistence.id,
                    "name": persistence.name,
                    "user_id": persistence.user_id,
                    "category": persistence.category,
                    "amount": persistence.amount,
                    "currency": persistence.currency,
                    "note": persistence.note,
                    "date": persistence.date,
                }
            )
            for persistence in persistence_output
        ]

        if highest_spent_output is not None:
            highest_spent_output = ExpenseReadModel(
                {
                    "id": highest_spent_output.id,
                    "name": highest_spent_output.name,
                    "user_id": highest_spent_output.user_id,
                    "category": highest_spent_output.category,
                    "amount": highest_spent_output.amount,
                    "currency": highest_spent_output.currency,
                    "note": highest_spent_output.note,
                    "date": highest_spent_output.date,
                }
            )

        overview_read_model = ExpenseOverviewReadModel(
            {
                "user_id": user_id,
                "recent_expenses": read_model,
                "total_spent": total_spent_output if total_spent_output else 0,
                "highest_expense": highest_spent_output,
            }
        )

        return result_ok(overview_read_model)

    async def first(self, options: GetOptions) -> Either[
        ExpenseReadModel,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:
        if filter := options.get("filter"):
            user_id = filter.get("user_id")

            if user_id is None:
                return result_fail(
                    RepositoryUnexpectedError(
                        Exception("User ID is required in filter for first method")
                    )
                )

        result = await self.db.scalars(
            select(Expense).filter_by(**options.get("filter", {}))
        )

        persistence_output = result.first()

        if not persistence_output:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        read_model = ExpenseReadModel(
            {
                "id": persistence_output.id,
                "name": persistence_output.name,
                "user_id": persistence_output.user_id,
                "category": persistence_output.category,
                "amount": persistence_output.amount,
                "currency": persistence_output.currency,
                "note": persistence_output.note,
                "date": persistence_output.date,
            }
        )

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
