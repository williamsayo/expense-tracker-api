from fastapi import Depends, UploadFile, File
from typing import Self
from dataclasses import dataclass, fields
from src.core.config import get_settings, Settings
from src.shared.application.dtos.upload import FileUploadDTO
from src.shared.application.services.image_validation import ImageValidationService
from src.shared.infrastructure.adapters.ports import repository, cdn
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


async def _run_image_validation(file) -> FileUploadDTO:
    validation_service = ImageValidationService(file)
    validation_result = await validation_service.validate_file()
    return validation_result.unwrap_or_raise()


async def validate_image_upload(
    file: UploadFile = File(..., description="Image file to be uploaded"),
) -> FileUploadDTO:
    return await _run_image_validation(file)


async def validate_optional_image_upload(
    file: UploadFile | None = File(
        None, description="Optional image file to be uploaded"
    ),
) -> FileUploadDTO | None:
    if file is None:
        return None
    return await _run_image_validation(file)
