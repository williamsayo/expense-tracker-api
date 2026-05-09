from typing import Sequence
from uuid import UUID
from boilerplate import (
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
from result import Either, result_ok, result_fail
from spending.budgeting.domain.entities.budget_entity import BudgetEntity


class LocalBudgetRepository(
    WriteRepository[BudgetEntity, UniqueEntityId],
    ReadRepository[BudgetEntity],
):
    """Repository implementation for budget data."""

    db: dict[str | UUID, BudgetEntity] = {}

    async def add(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        """Adds a new budget entity to the database."""
        for key, budget in self.db.items():
            if (
                key != aggregate.id
                and budget.budget_period.start_date
                == aggregate.budget_period.start_date
            ):
                return result_fail(
                    ConflictError(
                        Exception("Budget for this period already exists"),
                        "Budget for this period already exists",
                    )
                )

        self.db[aggregate.id.value] = aggregate
        return result_ok()

    async def exists(self, aggregate_id: UniqueEntityId) -> bool:
        result = aggregate_id.value in self.db
        return result

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetEntity,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Retrieves a budget entity by its unique identifier."""

        result = self.db.get(aggregate_id.value)

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        return result_ok(result)

    async def list(
        self, options: GetAllOptions
    ) -> Either[Sequence[BudgetEntity], RepositoryUnexpectedError | DataIntegrityError]:

        result: list[BudgetEntity] = []

        if filter := options.get("filter"):
            user_id = filter.get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required"),
                    "User ID filter is required",
                )
            )

        for budget in self.db.values():
            if budget.user_id == user_id:
                result.append(budget)

        return result_ok(result)

    async def first(self, options: GetOptions) -> Either[
        BudgetEntity,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        result: BudgetEntity | None = None
        
        if filter := options.get("filter"):
            user_id = filter.get("user_id")

        if user_id is None:
            return result_fail(
                RepositoryUnexpectedError(
                    Exception("User ID filter is required"),
                    "User ID filter is required",
                )
            )

        for budget in self.db.values():
            if budget.user_id == user_id:
                result = budget

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        return result_ok(result)

    async def remove(
        self, aggregate: BudgetEntity
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...
