from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends
from boilerplate import CommandDependency, IEventDispatcher
from src.shared.infrastructure.db.dependencies import AsyncSessionLocal
from src.spending.shared.infrastructure.uow.unit_of_work import SpendingUnitOfWork
from src.shared.application.events.dispatcher.dependencies import get_event_dispatcher
from src.shared.utils.setup_dependencies import get_cdn_service, get_object_storage
from src.shared.infrastructure.adapters.ports import repository, cdn as cdn_protocol
from src.spending.expenses.infrastructure.services.openai.openai_service import (
    OpenAIService,
)
from src.spending.expenses.infrastructure.adapters.ports.llm import LLMServiceProtocol


def get_spending_unit_of_work() -> SpendingUnitOfWork:
    """Factory function to create an instance of SpendingUnitOfWork."""
    return SpendingUnitOfWork(AsyncSessionLocal)


@dataclass(slots=True)
class SpendingDependencies(CommandDependency):
    """Dependency container for Spending use cases."""

    uow: SpendingUnitOfWork = Depends(get_spending_unit_of_work)
    cdn: cdn_protocol.CDNService = Depends(get_cdn_service)
    media_repo: repository.ObjectStorageRepository = Depends(get_object_storage)
    llm: LLMServiceProtocol = Depends(OpenAIService)
    eventPublisher: IEventDispatcher = Depends(get_event_dispatcher)

SpendingDeps = Annotated[SpendingDependencies, Depends()]
