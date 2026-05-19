from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from boilerplate import CommandDependency, IEventBus
from src.shared.infrastructure.db.dependencies import get_session
from src.spending.shared.infrastructure.uow.unit_of_work import SpendingUnitOfWork
from src.shared.infrastructure.dispatcher.dependencies import get_event_bus


def get_spending_unit_of_work(
    session: AsyncSession = Depends(get_session),
) -> SpendingUnitOfWork:
    """Factory function to create an instance of SpendingUnitOfWork."""
    return SpendingUnitOfWork(session)

@dataclass(slots=True)
class SpendingDependencies(CommandDependency):
    """Dependency container for Spending use cases."""

    uow: SpendingUnitOfWork = Depends(get_spending_unit_of_work)
    eventPublisher: IEventBus = Depends(get_event_bus)


SpendingDeps = Annotated[SpendingDependencies, Depends()]