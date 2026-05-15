from dataclasses import dataclass
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.core.config import settings
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_session, get_dynamodb
from src.spending.budgeting.infrastructure.repositories.postgres.budget_repo import (
    BudgetRepository,
)
from src.spending.budgeting.infrastructure.repositories.local.budget_repo import (
    LocalBudgetRepository,
)
from src.spending.budgeting.infrastructure.repositories.postgres.budget_read_repo import (
    BudgetReadRepository,
)
from src.spending.budgeting.infrastructure.repositories.local.budget_read_repo import (
    LocalBudgetReadRepository,
)
from src.spending.budgeting.infrastructure.adapters.ports.repository import (
    BudgetRepositoryProtocol,
    BudgetReadRepositoryProtocol,
)
from src.shared.infrastructure.dispatcher.event_bus import EventBus
from src.shared.infrastructure.dispatcher.dependencies import get_event_bus


def get_budget_repository(
    dynamodb_resource: AsyncSession = Depends(get_dynamodb),
) -> BudgetRepositoryProtocol:
    """Factory function to create a BudgetRepository instance."""
    return BudgetRepository(dynamodb_resource)


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
    dispatcher: EventBus = Depends(get_event_bus)


@dataclass(slots=True)
class BudgetReadDependencies(BaseDependency):
    """Dependency container for example use cases."""

    repo: BudgetReadRepositoryProtocol = Depends(get_budget_read_repository)


BudgetDeps = Annotated[BudgetDependencies, Depends()]
BudgetReadDeps = Annotated[BudgetReadDependencies, Depends()]
