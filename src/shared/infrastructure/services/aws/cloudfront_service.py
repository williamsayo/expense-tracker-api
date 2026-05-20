from types_aiobotocore_cloudfront import CloudFrontClient
from result import result_fail, result_ok, Either
from boilerplate import UnexpectedError
from src.core.config import get_settings
from src.shared.infrastructure.services.aws.utils import (
    generate_bucket_url,
    signed_url,
    invalidate_cache,
)

settings = get_settings()
class CloudFrontService:

    def __init__(self, client: CloudFrontClient):
        self.client = client

    async def invalidate_cache(self, key: str) -> Either[None, UnexpectedError]:
        try:
            await invalidate_cache(self.client, key)
            return result_ok(None)
        except Exception as error:
            return result_fail(UnexpectedError(error))

    def signed_url(self, key: str) -> Either[str, UnexpectedError]:
        try:
            url = generate_bucket_url(key)
            return result_ok(signed_url(url))
        except Exception as error:
            return result_fail(UnexpectedError(error))

    def generate_url(self, key: str) -> str:
        return f"{settings.media_url}/{key}"
