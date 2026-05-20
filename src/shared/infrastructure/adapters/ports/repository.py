from typing import BinaryIO, Protocol, overload
from boilerplate import UnexpectedError
from result import Either


class ObjectStorageRepository(Protocol):
    async def upload_avatar(
        self, key: str, file: BinaryIO
    ) -> Either[str, UnexpectedError]: ...

    async def upload_receipt(
        self, key: str, file: BinaryIO
    ) -> Either[str, UnexpectedError]: ...
