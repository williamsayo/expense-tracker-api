from dataclasses import dataclass
from types_aiobotocore_dynamodb import DynamoDBServiceResource
from typing_extensions import Annotated
from fastapi import Depends
from src.dashboard.application.ports.dependencies import OverviewDependencies
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.services.aws.dependencies import get_dynamodb_client
from src.dashboard.infrastructure.adapters.ports.repository import (
    DashboardRepositoryProtocol,
)
from src.dashboard.infrastructure.repositories.dynamodb.dynamodb_read_repo import (
    DynamoDbReadRepository,
)


async def get_dashboard_repository(
    client: DynamoDBServiceResource = Depends(get_dynamodb_client),
) -> DashboardRepositoryProtocol:
    """Factory function to create a dashboard repository instance."""
    repository = await DynamoDbReadRepository.create(client)
    return repository.unwrap_or_raise()


@dataclass(slots=True)
class OverviewDependency(BaseDependency):
    repository: DashboardRepositoryProtocol = Depends(get_dashboard_repository)


OverviewDeps = Annotated[OverviewDependencies, Depends(OverviewDependency)]
