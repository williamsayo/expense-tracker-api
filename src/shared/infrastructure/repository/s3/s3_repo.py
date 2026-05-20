from enum import StrEnum
from typing import BinaryIO
from types_aiobotocore_s3 import S3Client
from result import result_fail, result_ok, Either
from boilerplate import UnexpectedError
from src.shared.infrastructure.services.aws.utils import (
    create_bucket,
    generate_object_url,
)
from src.core.config import Settings


class FolderPath(StrEnum):
    receipts = "receipts"
    avatars = "avatars"


class S3BucketRepository:

    def __init__(self, client: S3Client, settings: Settings):
        self.client = client
        self.settings = settings
        self.bucket_name = settings.aws_s3_bucket_name

    async def create_bucket(self, bucket_name: str):
        await create_bucket(bucket_name, self.client)

    async def upload_avatar(
        self, key: str, file: BinaryIO
    ) -> Either[str, UnexpectedError]:
        key = self.construct_key(key, FolderPath.avatars)
        await self.upload_file_object(key=key, data=file)
        return result_ok(generate_object_url(key))

    async def upload_receipt(
        self, key: str, file: BinaryIO
    ) -> Either[str, UnexpectedError]:
        key = self.construct_key(key, FolderPath.receipts)
        await self.upload_file_object(key=key, data=file)
        return result_ok(generate_object_url(key))

    async def upload_file_object(
        self,
        key: str,
        data: BinaryIO,
    ) -> Either[str, UnexpectedError]:
        try:
            await self.client.upload_fileobj(
                Bucket=self.bucket_name,
                Key=key,
                Fileobj=data,
            )
            return result_ok(generate_object_url(key))
        except Exception as error:
            return result_fail(UnexpectedError(error))

    async def put_object(
        self, key: str, data: bytes, *, location: FolderPath
    ) -> Either[str, UnexpectedError]:
        try:
            await self.client.put_object(
                Bucket=self.bucket_name,
                Key=f"{location}/{key}",
                Body=data,
            )

            return result_ok(generate_object_url(key))

        except Exception as error:
            return result_fail(UnexpectedError(error))

    async def delete_object(self, key: str) -> Either[None, UnexpectedError]:
        try:
            await self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return result_ok(None)
        except Exception as error:
            return result_fail(UnexpectedError(error))

    async def get_object(self, key: str) -> Either[bytes, UnexpectedError]:
        try:
            response = await self.client.get_object(Bucket=self.bucket_name, Key=key)
            return result_ok(await response["Body"].read())
        except Exception as error:
            return result_fail(UnexpectedError(error))

    async def presigned_url(self, key: str) -> Either[str, UnexpectedError]:
        try:
            url = await self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=3600,
            )
            return result_ok(url)
        except Exception as error:
            return result_fail(UnexpectedError(error))

    def construct_key(self, filename: str, folder: FolderPath) -> str:
        return f"{folder}/{filename}"
