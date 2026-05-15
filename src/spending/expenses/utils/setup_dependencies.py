from dataclasses import dataclass
from boilerplate import CommandDependency, IEventBus
from fastapi import Depends
from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_session, get_dynamodb
from src.spending.expenses.infrastructure.repositories.dynamodb.expense_repo import (
    ExpenseRepository,
)
from src.spending.expenses.infrastructure.repositories.dynamodb.expense_read_repo import (
    ExpenseReadRepository,
)
from src.spending.expenses.infrastructure.adapters.ports.repository import (
    ExpenseRepositoryProtocol,
    ExpenseReadRepositoryProtocol,
)
from src.shared.infrastructure.dispatcher.event_bus import EventBus
from src.shared.infrastructure.dispatcher.dependencies import get_event_bus


def get_expense_read_repository(
    db: AsyncSession = Depends(get_session),
) -> ExpenseReadRepositoryProtocol:
    """Factory function to select the appropriate ExpenseReadRepository based on settings."""
    return ExpenseReadRepository(db)


def get_expense_repository(
    resource: Any = Depends(get_dynamodb),
) -> ExpenseRepositoryProtocol:
    """Factory function to select the appropriate ExpenseRepository based on settings."""
    return ExpenseRepository(resource)


@dataclass(slots=True)
class ExpenseDependencies(CommandDependency):
    """Dependency container for Spending use cases."""

    expense_repo: ExpenseRepository = Depends(get_expense_repository)
    eventPublisher: IEventBus = Depends(get_event_bus)


@dataclass(slots=True)
class ExpenseReadDependencies(BaseDependency):
    """Dependency container for expense use cases."""

    repo: ExpenseReadRepositoryProtocol = Depends(get_expense_read_repository)
    dispatcher: EventBus = Depends(get_event_bus)


ExpenseDeps = Annotated[ExpenseDependencies, Depends()]
ExpenseReadDeps = Annotated[ExpenseReadDependencies, Depends()]
