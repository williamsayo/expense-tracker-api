from dataclasses import dataclass
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from boilerplate import IEventDispatcher
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_session
from src.spending.budgeting.infrastructure.repositories.postgres.budget_repo import (
    BudgetRepository,
)
from src.spending.budgeting.infrastructure.repositories.postgres.budget_read_repo import (
    BudgetReadRepository,
)
from src.spending.budgeting.infrastructure.adapters.ports.repository import (
    BudgetRepositoryProtocol,
    BudgetReadRepositoryProtocol,
)
from src.shared.application.events.dispatcher.dependencies import get_event_dispatcher


def get_budget_repository(
    db: AsyncSession = Depends(get_session),
) -> BudgetRepositoryProtocol:
    """Factory function to create a BudgetRepository instance."""
    # if settings.use_local_repository:
    #     return LocalBudgetRepository()
    return BudgetRepository(db)


def get_budget_read_repository(
    db: AsyncSession = Depends(get_session),
) -> BudgetReadRepositoryProtocol:
    """Factory function to create a BudgetReadRepository instance."""
    # if settings.use_local_repository:
    #     return LocalBudgetReadRepository()
    return BudgetReadRepository(db)


@dataclass(slots=True)
class BudgetDependencies(BaseDependency):
    """Dependency container for example use cases."""

    repo: BudgetRepositoryProtocol = Depends(get_budget_repository)
    dispatcher: IEventDispatcher = Depends(get_event_dispatcher)


@dataclass(slots=True)
class BudgetReadDependencies(BaseDependency):
    """Dependency container for example use cases."""

    repo: BudgetReadRepositoryProtocol = Depends(get_budget_read_repository)
    event_dispatcher: IEventDispatcher = Depends(get_event_dispatcher)


BudgetDeps = Annotated[BudgetDependencies, Depends()]
BudgetReadDeps = Annotated[BudgetReadDependencies, Depends()]
