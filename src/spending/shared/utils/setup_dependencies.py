from dataclasses import dataclass
from typing import Annotated
from fastapi import Depends
from boilerplate import CommandDependency, IEventBus
from src.shared.infrastructure.db.dependencies import AsyncSessionLocal
from src.spending.shared.infrastructure.uow.unit_of_work import SpendingUnitOfWork
from src.shared.infrastructure.dispatcher.dependencies import get_event_bus
from src.shared.utils.setup_dependencies import get_cdn_service, get_object_storage
from src.shared.infrastructure.adapters.ports import repository, cdn as cdn_protocol
from src.spending.expenses.infrastructure.services.openai.openai_service import (
    OpenAIService,
)
from src.spending.expenses.infrastructure.services.google_cloud.google_cloud_service import (
    GoogleCloudVisionService,
)


def get_spending_unit_of_work() -> SpendingUnitOfWork:
    """Factory function to create an instance of SpendingUnitOfWork."""
    return SpendingUnitOfWork(AsyncSessionLocal)

@dataclass(slots=True)
class SpendingDependencies(CommandDependency):
    """Dependency container for Spending use cases."""

    uow: SpendingUnitOfWork = Depends(get_spending_unit_of_work)
    cdn: cdn_protocol.CDNService = Depends(get_cdn_service)
    media_repo: repository.ObjectStorageRepository = Depends(get_object_storage)
    llm: OpenAIService = Depends(OpenAIService)
    eventPublisher: IEventBus = Depends(get_event_bus)


SpendingDeps = Annotated[SpendingDependencies, Depends()]
