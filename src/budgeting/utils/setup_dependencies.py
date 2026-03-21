from dataclasses import dataclass
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from shared.utils.setup_dependencies import BaseDependency
from shared.infrastructure.db.dependencies import get_session
from budgeting.infrastructure.repositories.postgres.budget_repo import BudgetRepository
from budgeting.infrastructure.repositories.base import BudgetingRepositoryProtocol


def get_budget_repository(db: AsyncSession = Depends(get_session)) -> BudgetRepository:
    """Factory function to create a BudgetRepository instance."""
    return BudgetRepository(db)


@dataclass(slots=True, frozen=True)
class BudgetDependencies(BaseDependency):
    """Dependency container for example use cases."""
    repo: BudgetingRepositoryProtocol = Depends(get_budget_repository)


BudgetDeps = Annotated[BudgetDependencies, Depends()]
