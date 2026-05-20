from typing import AsyncGenerator, TYPE_CHECKING
from src.shared.infrastructure.services.aws.config import get_aioboto3_session

if TYPE_CHECKING:
    from types_aiobotocore_cloudfront import CloudFrontClient
    from types_aiobotocore_s3 import S3Client


async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    async with get_aioboto3_session().client("s3") as s3_client:
        yield s3_client

async def get_cloudfront_client() -> AsyncGenerator[CloudFrontClient, None]:
    async with get_aioboto3_session().client("cloudfront") as cloudfront_client:
        yield cloudfront_client