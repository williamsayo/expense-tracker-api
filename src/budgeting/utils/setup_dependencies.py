from dataclasses import dataclass
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.config import settings
from shared.utils.setup_dependencies import BaseDependency
from shared.infrastructure.db.dependencies import get_session
from budgeting.infrastructure.repositories.postgres.budget_repo import BudgetRepository
from budgeting.infrastructure.repositories.local.budget_repo import (
    LocalBudgetRepository,
)
from budgeting.infrastructure.repositories.base import BudgetRepositoryProtocol


def get_budget_repository(db: AsyncSession = Depends(get_session)) -> BudgetRepository:
    """Factory function to create a BudgetRepository instance."""
    return BudgetRepository(db)

def get_budget_repository_dependency() -> BudgetRepositoryProtocol:
    """Factory function to select the appropriate BudgetRepository based on settings."""
    if settings.use_local_repository:
        return LocalBudgetRepository()
    return get_budget_repository()


@dataclass(slots=True, frozen=True)
class BudgetDependencies(BaseDependency):
    """Dependency container for example use cases."""

    repo: BudgetRepositoryProtocol = Depends(get_budget_repository_dependency)


BudgetDeps = Annotated[BudgetDependencies, Depends()]
