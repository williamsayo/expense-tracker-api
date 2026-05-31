from typing_extensions import Protocol
from src.dashboard.infrastructure.adapters.ports.repository import (
    DashboardRepositoryProtocol,
)


class OverviewDependencies(Protocol):
    """Protocol defining the dependencies required by dashboard use cases."""

    repository: DashboardRepositoryProtocol
