from dataclasses import dataclass
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from shared.utils.setup_dependencies import BaseDependency
from shared.infrastructure.db.dependencies import get_session
from expenses.infrastructure.repositories.postgres.expense_repo import ExpenseRepository
from expenses.infrastructure.repositories.postgres.expense_read_repo import (
    ExpenseReadRepository,
)
from expenses.infrastructure.repositories.local.expense_repo import (
    LocalExpenseRepository,
)
from expenses.infrastructure.adapters.ports.repository import (
    ExpenseRepositoryProtocol,
    ExpenseReadRepositoryProtocol,
)
from shared.infrastructure.dispatcher.event_bus import EventBus
from shared.infrastructure.dispatcher.dependencies import get_event_bus


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
    dispatcher: EventBus = Depends(get_event_bus)


@dataclass(slots=True)
class ExpenseReadDependencies(BaseDependency):
    """Dependency container for expense use cases."""

    repo: ExpenseReadRepositoryProtocol = Depends(get_expense_read_repository)
    dispatcher: EventBus = Depends(get_event_bus)


ExpenseDeps = Annotated[ExpenseDependencies, Depends()]
ExpenseReadDeps = Annotated[ExpenseReadDependencies, Depends()]
