from dataclasses import dataclass
from fastapi import Depends
from typing import Annotated
from boilerplate import IEventDispatcher
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_session
from src.spending.expenses.application.ports.dependencies import ExpenseCommandDeps, ExpenseQueryDeps
from src.spending.expenses.infrastructure.repositories.postgres.expense_repo import (
    ExpenseRepository,
)
from src.spending.expenses.infrastructure.repositories.postgres.expense_read_repo import (
    ExpenseReadRepository,
)
from src.spending.expenses.infrastructure.adapters.ports.repository import (
    ExpenseRepositoryProtocol,
    ExpenseReadRepositoryProtocol,
)
from src.shared.infrastructure.adapters.ports.repository import ObjectStorageRepository
from src.shared.application.events.dispatcher.dependencies import get_event_dispatcher
from src.shared.infrastructure.adapters.ports.cdn import CDNService
from src.shared.utils.setup_dependencies import get_cdn_service,get_object_storage

def get_expense_read_repository(
    db: AsyncSession = Depends(get_session),
) -> ExpenseReadRepositoryProtocol:
    """Factory function to select the appropriate ExpenseReadRepository based on settings."""
    return ExpenseReadRepository(db)


def get_expense_repository(
    db: AsyncSession = Depends(get_session),
) -> ExpenseRepositoryProtocol:
    """Factory function to select the appropriate ExpenseRepository based on settings."""
    # if settings.use_local_repository:
    #     return LocalExpenseRepository()
    return ExpenseRepository(db)

@dataclass(slots=True)
class ExpenseDependencies(BaseDependency):
    """Dependency container for expense use cases."""

    repo: ExpenseRepositoryProtocol = Depends(get_expense_repository)
    object_storage: ObjectStorageRepository = Depends(get_object_storage)
    cdn: CDNService = Depends(get_cdn_service)
    dispatcher: IEventDispatcher = Depends(get_event_dispatcher)


@dataclass(slots=True)
class ExpenseReadDependencies(BaseDependency):
    """Dependency container for expense use cases."""

    repo: ExpenseReadRepositoryProtocol = Depends(get_expense_read_repository)
    cdn: CDNService = Depends(get_cdn_service)
    dispatcher: IEventDispatcher = Depends(get_event_dispatcher)


ExpenseDeps = Annotated[ExpenseCommandDeps, Depends(ExpenseDependencies)]
ExpenseReadDeps = Annotated[ExpenseQueryDeps, Depends(ExpenseReadDependencies)]
