from sqlalchemy import select, exists, and_, func
from sqlalchemy.orm import selectinload
from typing import Sequence, cast
from uuid import UUID
from boilerplate import (
    AsyncReadRepository,
    ConcurrencyError,
    ConflictError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
    GetAllOptions,
    GetOptions,
)
from sqlalchemy.ext.asyncio import AsyncSession
from result import Either, is_fail, result_ok, result_fail
from spending.budgeting.domain.read_models.budget_summary import BudgetSummaryReadModel
from spending.budgeting.domain.read_models.budget_overview import (
    BudgetOverviewReadModel,
)
from spending.budgeting.infrastructure.repositories.schema import (
    Budget,
    BudgetAllocation,
)
from spending.budgeting.infrastructure.mappers.budget_summary_mapper import (
    BudgetSummaryMapper,
)


class BudgetReadRepository(AsyncReadRepository[BudgetSummaryReadModel]):
    """Repository implementation for budget data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]:
        """Adds a new budget entity to the database."""
        persistence = BudgetSummaryMapper.to_persistence(aggregate)
        exists = await self.exists(aggregate.budget_id)

        if is_fail(exists):
            return result_fail(exists.value)

        if exists:
            await self.db.merge(persistence)
        else:
            self.db.add(persistence)

        await self.db.commit()

        return result_ok()

    async def exists(
        self, aggregate_id: UUID | str
    ) -> Either[bool, RepositoryUnexpectedError]:
        statement = select(exists().where(Budget.id == aggregate_id))
        result = await self.db.scalar(statement)
        return result_ok(cast(bool, result))

    async def get_by_id(self, aggregate_id: UUID | str) -> Either[
        BudgetSummaryReadModel,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Retrieves a budget entity by its unique identifier."""

        statement = (
            select(Budget)
            .where(Budget.id == aggregate_id)
            .options(selectinload(Budget.allocations))
        )
        result = (await self.db.scalars(statement)).one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetSummaryMapper.to_read_model(result)

        return result_ok(entity_result)

    async def list(
        self, options: GetAllOptions[str]
    ) -> Either[
        Sequence[BudgetSummaryReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]:
        statement = select(Budget).options(
            selectinload(Budget.allocations), selectinload(Budget.expenses)
        )

        if filter := options.get("filter"):
            statement = statement.filter_by(**filter)

        if limit := options.get("limit"):
            statement = statement.limit(limit)

        if sort := options.get("sort"):
            statement = statement.order_by(
                *[
                    (
                        getattr(Budget, col).desc()
                        if direction == "desc"
                        else getattr(Budget, col).asc()
                    )
                    for col, direction in sort.items()
                ]
            )

        result = await self.db.scalars(statement)
        persistence_output = result.all()

        result = tuple(
            BudgetSummaryMapper.to_read_model(persistence)
            for persistence in persistence_output
        )

        return result_ok(result)

    async def first(self, options: GetOptions) -> Either[
        BudgetSummaryReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:
        statement = select(Budget).options(selectinload(Budget.allocations))

        if filter := options.get("filter"):
            if "expense_date" in filter:
                date = filter.pop("expense_date")
                statement = statement.where(
                    and_(
                        Budget.start_date <= date,
                        Budget.end_date >= date,
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

        entity_result = BudgetSummaryMapper.to_read_model(persistence_output)

        return result_ok(entity_result)

    async def remove(
        self, aggregate: BudgetSummaryReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def get_budget_overview(self, options: GetAllOptions[str]) -> Either[
        BudgetOverviewReadModel,
        RepositoryUnexpectedError,
    ]:
        statement = select(Budget).options(selectinload(Budget.allocations))

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

        recent_budgets = statement.order_by(Budget.start_date.desc()).limit(
            options.get("limit", 5)
        )

        active_budget = statement.where(
            and_(
                Budget.user_id == user_id,
                Budget.start_date <= func.current_date(),
                Budget.end_date >= func.current_date(),
            )
        ).order_by(Budget.start_date.desc())

        total_budgeted = (
            select(func.sum(BudgetAllocation.amount).label("total_budgeted"))
            .join(
                Budget,
                Budget.id == BudgetAllocation.budget_id,
            )
            .where(Budget.user_id == user_id)
        )

        upcoming_budget = statement.where(
            and_(
                Budget.user_id == user_id,
                Budget.start_date > func.current_date(),
            )
        ).order_by(Budget.start_date.asc())

        result = await self.db.scalars(recent_budgets)
        persistence_output = result.all()

        upcoming_budget_result = await self.db.scalars(upcoming_budget)
        upcoming_budget_output = upcoming_budget_result.first()

        active_budget_result = await self.db.scalars(active_budget)
        active_budget_output = active_budget_result.first()

        total_budgeted_result = await self.db.scalars(total_budgeted)
        total_budgeted_output = total_budgeted_result.first()

        read_model = [
            BudgetSummaryMapper.to_read_model(persistence)
            for persistence in persistence_output
        ]

        if upcoming_budget_output is not None:
            upcoming_budget_output = BudgetSummaryMapper.to_read_model(
                upcoming_budget_output
            )

        if active_budget_output is not None:
            active_budget_output = BudgetSummaryMapper.to_read_model(
                active_budget_output
            )

        overview_read_model = BudgetOverviewReadModel(
            {
                "user_id": user_id,
                "recent_budgets": read_model,
                "total_allocated": (
                    total_budgeted_output if total_budgeted_output else 0
                ),
                "upcoming_budget": upcoming_budget_output,
                "active_budget": active_budget_output,
            }
        )

        return result_ok(overview_read_model)
