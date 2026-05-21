from typing import Protocol
from result import Either
from boilerplate import BadRequestError
from src.shared.application.dtos.upload import FileUploadDTO


class ImageValidation(Protocol):
    async def validate_file(self) -> Either[FileUploadDTO, BadRequestError]: ...
