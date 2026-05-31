from typing import Protocol
from boilerplate import IEventDispatcher
from src.shared.infrastructure.adapters.ports.cdn import CDNService
from src.shared.infrastructure.adapters.ports.repository import ObjectStorageRepository
from src.spending.expenses.infrastructure.adapters.ports.repository import (
    ExpenseReadRepositoryProtocol,
    ExpenseRepositoryProtocol,
)


class ExpenseCommandDeps(Protocol):
    """Protocol defining the dependencies required by expense command use cases."""

    repo: ExpenseRepositoryProtocol
    object_storage: ObjectStorageRepository
    cdn: CDNService
    dispatcher: IEventDispatcher


class ExpenseQueryDeps(Protocol):
    """Protocol defining the dependencies required by expense query use cases."""

    repo: ExpenseReadRepositoryProtocol
    cdn: CDNService
    dispatcher: IEventDispatcher
