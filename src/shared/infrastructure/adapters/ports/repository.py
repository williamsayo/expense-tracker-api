from typing import BinaryIO, Protocol, overload
from boilerplate import UnexpectedError
from result import Either


class ObjectStorageRepository(Protocol):
    async def upload_avatar(
        self,
        key: str,
        file: BinaryIO,
        *,
        content_type: str = "image/png",
        username: str | None = None,
        user_id: str | None = None,
        original_filename: str | None = None,
    ) -> Either[str, UnexpectedError]: ...

    async def upload_receipt(
        self,
        key: str,
        file: BinaryIO,
        *,
        content_type: str = "application/pdf",
        username: str | None = None,
        user_id: str | None = None,
        original_filename: str | None = None,
    ) -> Either[str, UnexpectedError]: ...
