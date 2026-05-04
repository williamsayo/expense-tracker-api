from typing import List
from uuid import UUID
from boilerplate import (
    DataIntegrityError,
    RepositoryUnexpectedError,
    ConflictError,
    ConcurrencyError,
    RepositoryNotFoundError,
    AuthenticationError,
    WriteRepository,
    ReadRepository,
    UniqueEntityId,
    GetAllOptions,
    GetOptions,
    GetAllOptions,
    GetOptions,
)
from result import result_fail, result_ok, Either
from shared.domain.types.user_id import UserId
from expenses.domain.entities.expense_entity import ExpenseEntity


class LocalExpenseRepository(WriteRepository, ReadRepository):
    """Repository implementation for expense data."""

    db: dict[str | UUID, ExpenseEntity] = {}

    async def list(
        self, options: GetAllOptions
    ) -> Either[List[ExpenseEntity], RepositoryUnexpectedError]:
        result: List[ExpenseEntity] = []
        if filter := options.get("filter"):
            user_id = filter.get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID is required in filter for list method")
                )
            )

        for expense in self.db.values():
            if expense.user_id == user_id:
                result.append(expense)

        return result_ok(result)

    async def get_by_id(self, aggregateId: UniqueEntityId) -> Either[
        ExpenseEntity,
        RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError,
    ]:

        result = self.db.get(aggregateId.value)

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        return result_ok(result)

    async def add(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError | ConflictError | ConcurrencyError]:

        for key, expense in self.db.items():
            if (
                key != aggregate.id.value
                and expense.category.name == aggregate.category.name
                and expense.user_id == aggregate.user_id
            ):
                return result_fail(
                    ConflictError(
                        Exception("Expense with this category already exists"),
                        "Expense with this category already exists",
                    )
                )

        self.db[aggregate.id.value] = aggregate
        return result_ok()

    async def exists(self, aggregateId: UniqueEntityId) -> bool:
        query = aggregateId.value in self.db
        return query

    async def first(self, options: GetOptions) -> Either[
        ExpenseEntity,
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

        for expense in self.db.values():
            if expense.user_id == user_id:
                result = expense
                break

        if not result:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Expense not found"), "Expense not found"
                )
            )

        return result_ok(result)

    async def remove(
        self, aggregate: ExpenseEntity
    ) -> Either[None, RepositoryUnexpectedError]:
        result = self.db.pop(aggregate.id.value, None)

        if result is None:
            return result_fail(
                RepositoryUnexpectedError(Exception("Expense not found for removal"))
            )

        return result_ok()

    async def remove_all(
        self, category: str, user_id: UserId
    ) -> Either[int, RepositoryUnexpectedError | AuthenticationError]:

        deleted_count = 0

        for expense in self.db.values():
            if expense.category == category and expense.user_id == user_id:
                del self.db[expense.id.value]
                deleted_count += 1

        return result_ok(deleted_count)
