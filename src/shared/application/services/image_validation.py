from typing import Text
import uuid
from fastapi import UploadFile
from boilerplate import (
    CoreError,
    ApplicationError,
    BadRequestError,
    BadGatewayError,
    UnexpectedError,
)
from result import result_combine, result_ok, result_fail, is_fail, Either
from pathlib import Path
import magic

from src.shared.application.dtos.upload import FileUploadDTO

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n": "image/png",
    b"RIFF": "image/webp",  # also check bytes 8-12 == b"WEBP"
    b"GIF87a": "image/gif",
    b"GIF89a": "image/gif",
}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class ImageValidationService:
    def __init__(self, file: UploadFile):
        self.file = file

    async def validate_file(self) -> Either[FileUploadDTO, BadRequestError]:
        file_size_result = await self.validate_file_size()
        declared_content_type = self.validate_content_type()
        content_type = await self.validate_magic_bytes(
            declared_content_type.value_or(None)
        )
        filename_result = self.validate_filename()

        combined_result = result_combine(
            (file_size_result, content_type, filename_result)
        )

        if is_fail(combined_result):
            return combined_result

        size, content_type, filename = combined_result.value

        filename, extension = filename

        unique_filename = self.make_unique_filename(extension)

        file = FileUploadDTO(
            file=self.file,
            filename=unique_filename,
            content_type=content_type,
            size=size,
            original_filename=filename,
        )

        return result_ok(file)

    async def validate_magic_bytes(
        self, declared_content_type: str | None
    ) -> Either[Text, BadRequestError]:
        """Validate the file's magic bytes to confirm its content type.
        Checks performed:
        - Read the first 512 bytes of the file
        - Use python-magic to detect the MIME type
        - Confirm the detected MIME type is allowed
        - If a declared content type is provided, confirm it matches the detected type
        Args:
            declared_content_type (str | None): The content type declared by the client, if any.
            Returns:
            Either[Text, BadRequestError]: Ok with detected MIME type or Fail with error.
        """
        header = await self.file.read(512)
        await self.file.seek(0)

        mime = magic.from_buffer(header, mime=True)
        if mime not in ALLOWED_CONTENT_TYPES:
            return result_fail(
                BadRequestError("File content does not match declared type")
            )

        if declared_content_type and mime != declared_content_type:
            return result_fail(
                BadRequestError("File content does not match declared type")
            )

        return result_ok(mime)

    def validate_content_type(self) -> Either[str | None, BadRequestError]:
        """Validate the declared content type of the uploaded file.
        Checks performed:
        - Presence of content type
        - Allowed content types

        Returns:
            Either[str | None, BadRequestError]: Ok with content type or Fail with error.
        """
        content_type = (
            self.file.content_type.strip().lower() if self.file.content_type else None
        )

        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            return result_fail(
                BadRequestError(f"Content type not allowed: {content_type}")
            )

        return result_ok(content_type)

    def validate_filename(
        self,
    ) -> Either[tuple[str | None, str], BadRequestError]:
        """Validate the filename for security and allowed extensions.

        Checks performed:
        - Null byte injection
        - Allowed extensions
        - Extracts the final extension for later use

        Returns:
           Either[tuple[str | None, str], BadRequestError]: Ok with (filename, extension) or Fail with error.
        """
        filename = self.file.filename

        if filename:
            name = Path(filename).name

            # Null bytes
            if "\x00" in name:
                return result_fail(BadRequestError("Invalid filename"))

            suffixes = Path(name).suffixes

            for ext in suffixes:
                if ext.lower() not in ALLOWED_EXTENSIONS:
                    return result_fail(
                        BadRequestError(f"Disallowed file extension: {ext}")
                    )

            final_ext = Path(name).suffix.lower()

            if final_ext not in ALLOWED_EXTENSIONS:
                return result_fail(
                    BadRequestError(f"Extension not allowed: {final_ext}")
                )

            return result_ok((name, final_ext))

        return result_ok((filename, ""))

    async def validate_file_size(self) -> Either[int, BadRequestError]:
        """Validate the file size by reading it in chunks.
        This approach avoids loading the entire file into memory, which is important for large files.
         Checks performed:
         - Read the file in 8KB chunks
         - Keep a running total of the file size
         - If the total exceeds the maximum allowed size, return an error
         Returns:
             Either[None, BadRequestError]: Ok if file size is within limits, or Fail with error.
        """
        file_size = 0

        while chunk := await self.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_SIZE_BYTES:
                return result_fail(BadRequestError("File size exceeds limit"))

        await self.file.seek(0)

        return result_ok(file_size)

    def make_unique_filename(self, extension: str) -> str:
        """Generate a unique filename using a UUID and the original file extension.
        This helps prevent filename collisions and can also obscure original filenames for security.
        Args:
            extension (str): The file extension to preserve.
        Returns:
            str: A unique filename with the original extension.
        """
        unique_suffix = uuid.uuid4().hex

        return f"{unique_suffix}{extension}"
