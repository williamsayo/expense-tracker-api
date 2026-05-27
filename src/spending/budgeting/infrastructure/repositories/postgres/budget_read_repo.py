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
from result import Either, result_ok, result_fail
from src.spending.budgeting.infrastructure.adapters.dto.budget import (
    BudgetReadModel,
)
from src.spending.budgeting.infrastructure.mappers.budget_read_mapper import (
    BudgetReadMapper,
)
from src.spending.budgeting.infrastructure.repositories.schema import (
    Budget,
    BudgetAllocation,
)
from src.shared.utils.build_query import AppFilter, build_query


class BudgetReadRepository(AsyncReadRepository[BudgetReadModel]):
    """Repository implementation for budget data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, aggregate: BudgetReadModel, *, auto_commit: bool = True
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def exists(
        self, aggregate_id: UUID | str
    ) -> Either[bool, RepositoryUnexpectedError]:
        statement = select(exists().where(Budget.id == aggregate_id))
        result = await self.db.scalar(statement)
        return result_ok(cast(bool, result))

    async def get_by_id(self, aggregate_id: UUID | str) -> Either[
        BudgetReadModel,
        RepositoryNotFoundError | RepositoryUnexpectedError | DataIntegrityError,
    ]:
        """Retrieves a budget entity by its unique identifier."""

        statement = (
            select(Budget)
            .where(Budget.id == aggregate_id)
            .options(
                selectinload(Budget.allocations),
                selectinload(Budget.expenses),
            )
        )
        result = (await self.db.scalars(statement)).one_or_none()

        if result is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetReadMapper.to_read_model(result)

        return result_ok(entity_result)

    async def list(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[
        Sequence[BudgetReadModel], RepositoryUnexpectedError | DataIntegrityError
    ]:
        statement = build_query(Budget, options).options(
            selectinload(Budget.allocations), selectinload(Budget.expenses)
        )

        result = await self.db.scalars(statement)
        persistence_output = result.all()

        result = [
            BudgetReadMapper.to_read_model(persistence)
            for persistence in persistence_output
        ]

        return result_ok(result)

    async def first(self, options: GetOptions[AppFilter]) -> Either[
        BudgetReadModel,
        RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError,
    ]:

        statement = build_query(Budget, options).options(
            selectinload(Budget.allocations),
            selectinload(Budget.expenses),
        )

        if "expense_date" in options.get("filter", {}):
            date = options["filter"].pop("expense_date")
            statement = statement.where(
                and_(
                    Budget.start_date <= date,
                    Budget.end_date >= date,
                )
            )

        persistence_output = (await self.db.scalars(statement)).one_or_none()

        if persistence_output is None:
            return result_fail(
                RepositoryNotFoundError(
                    Exception("Budget not found"), "Budget not found"
                )
            )

        entity_result = BudgetReadMapper.to_read_model(persistence_output)

        return result_ok(entity_result)

    # async def get_budget_overview(self, options: GetAllOptions[AppFilter]) -> Either[
    #     BudgetOverviewReadModel,
    #     RepositoryUnexpectedError,
    # ]:
    #     user_id = options.get("filter", {}).get("user_id")

    #     if user_id is None:
    #         return result_fail(
    #             RepositoryUnexpectedError(
    #                 Exception("User ID filter is required for overview"),
    #                 "User ID filter is required for overview",
    #             )
    #         )

    #     statement = build_query(Budget.__table__, options)

    #     recent_budgets = statement.order_by(
    #         Budget.__table__.columns.start_date.desc()
    #     ).limit(options.get("limit", 5))

    #     active_budget = statement.where(
    #         and_(
    #             Budget.__table__.columns.user_id == user_id,
    #             Budget.__table__.columns.start_date <= func.current_date(),
    #             Budget.__table__.columns.end_date >= func.current_date(),
    #         )
    #     ).order_by(Budget.__table__.columns.start_date.desc())

    #     total_budgeted = (
    #         select(func.sum(BudgetAllocation.amount).label("total_budgeted"))
    #         .join(
    #             Budget,
    #             Budget.id == BudgetAllocation.budget_id,
    #         )
    #         .where(Budget.user_id == user_id)
    #     )

    #     upcoming_budget = statement.where(
    #         and_(
    #             Budget.__table__.columns.user_id == user_id,
    #             Budget.__table__.columns.start_date > func.current_date(),
    #         )
    #     ).order_by(Budget.__table__.columns.start_date.asc())

    #     result = await self.db.execute(recent_budgets)
    #     persistence_output = result.mappings().all()

    #     upcoming_budget_result = await self.db.execute(upcoming_budget)
    #     upcoming_budget_output = upcoming_budget_result.mappings().first()

    #     active_budget_result = await self.db.execute(active_budget)
    #     active_budget_output = active_budget_result.mappings().first()

    #     total_budgeted_result = await self.db.scalars(total_budgeted)
    #     total_budgeted_output = total_budgeted_result.first()

    #     read_model = [
    #         BudgetSummaryReadModel(**persistence) for persistence in persistence_output
    #     ]

    #     if upcoming_budget_output is not None:
    #         upcoming_budget_output = BudgetSummaryReadModel(**upcoming_budget_output)

    #     if active_budget_output is not None:
    #         active_budget_output = BudgetSummaryReadModel(**active_budget_output)

    #     overview_read_model = BudgetOverviewReadModel(
    #         recent_budgets=read_model,
    #         total_allocated=(total_budgeted_output if total_budgeted_output else 0.0),
    #         upcoming_budget=upcoming_budget_output,
    #         active_budget=active_budget_output,
    #     )

    #     return result_ok(overview_read_model)

    async def remove(
        self, aggregate: BudgetReadModel
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def remove_all(
        self, options: GetAllOptions[AppFilter]
    ) -> Either[int, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    async def commit(self) -> Either[None, RepositoryUnexpectedError]:
        try:
            await self.db.commit()
            return result_ok()
        except Exception as error:
            await self.db.rollback()
            return result_fail(RepositoryUnexpectedError(error))
