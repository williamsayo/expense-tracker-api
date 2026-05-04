from typing import Sequence
from uuid import UUID
from boilerplate import (
    ConcurrencyError,
    ConflictError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    GetAllOptions,
    GetOptions,
    ReadRepository,
    UniqueEntityId,
)
from result import Either, result_ok, result_fail
from budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel


class LocalBudgetReadRepository(ReadRepository[BudgetSummaryReadModel]):
    """Repository implementation for budget data."""

    db: dict[str | UUID, BudgetSummaryReadModel] = {}

    async def add(
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        """Adds a new budget entity to the database."""
        for key, budget in self.db.items():
            if key != aggregate.budget_id and budget.start_date == aggregate.start_date:
                return result_fail(
                    ConflictError(
                        Exception("Budget for this period already exists"),
                        "Budget for this period already exists",
                    )
                )

        self.db[aggregate.budget_id] = aggregate
        return result_ok()

    async def exists(self, aggregate_id: UniqueEntityId) -> bool:
        result = aggregate_id.value in self.db
        return result

    async def get_by_id(self, aggregate_id: UniqueEntityId) -> Either[
        BudgetSummaryReadModel,
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

    async def list(self, options: GetAllOptions) -> Either[
        Sequence[BudgetSummaryReadModel],
        RepositoryUnexpectedError | DataIntegrityError,
    ]:

        result: list[BudgetSummaryReadModel] = []

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
        BudgetSummaryReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        result: BudgetSummaryReadModel | None = None

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
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...
