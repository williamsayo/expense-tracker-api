from fastapi import Depends
from typing import Self
from dataclasses import dataclass, fields
from src.core.config import get_settings, Settings
from src.shared.infrastructure.adapters.ports import repository,cdn
from src.shared.infrastructure.repository.s3.s3_repo import S3BucketRepository
from src.shared.infrastructure.services.aws.cloudfront_service import CloudFrontService
from src.shared.infrastructure.services.aws.dependencies import (
    get_s3_client,
    get_cloudfront_client,
    S3Client,
    CloudFrontClient,
)

@dataclass(slots=True)
class BaseDependency:
    """Base class for dependency containers."""

    def list_deps(self):
        return [getattr(self, field.name) for field in fields(self)]

    @classmethod
    def as_dependency(cls) -> Self:
        """Callable for FastAPI dependency injection."""
        return Depends(cls)


def get_object_storage(
    client: S3Client = Depends(get_s3_client),
    settings: Settings = Depends(get_settings),
) -> repository.ObjectStorageRepository:
    return S3BucketRepository(client, settings)


def get_cdn_service(
    client: CloudFrontClient = Depends(get_cloudfront_client),
) -> cdn.CDNService:
    return CloudFrontService(client)