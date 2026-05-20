from fastapi import UploadFile
from uuid import UUID
from result import Either, is_fail, result_fail, result_ok
from boilerplate import IllegalArgumentError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/gif"]


class FileValidator:
    @staticmethod
    def validate_file_size(file_size: int, max_size: int = MAX_FILE_SIZE) -> bool:
        if file_size <= max_size:
            return True
        return False

    @staticmethod
    def validate_file_type(file_type: str) -> bool:
        return file_type in ALLOWED_FILE_TYPES

    @staticmethod
    async def stream_file(
        file: UploadFile, max_size: int = MAX_FILE_SIZE
    ) -> Either[bytes, IllegalArgumentError]:
        file_content = bytearray()
        while chunk := await file.read(1024 * 1024):
            file_content.extend(chunk)
            if len(file_content) > max_size:
                return result_fail(
                    IllegalArgumentError(
                        None, f"File size exceeds the {max_size} limit"
                    )
                )
        await file.seek(0)  # Reset file pointer after reading
        return result_ok(bytes(file_content))

    @staticmethod
    async def stream_file_size(
        file: UploadFile, max_size: int = MAX_FILE_SIZE
    ) -> Either[int, IllegalArgumentError]:
        file_size = 0
        while chunk := await file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > max_size:
                return result_fail(
                    IllegalArgumentError(
                        None, f"File size exceeds the {max_size} limit"
                    )
                )
        await file.seek(0)
        return result_ok(file_size)

    @staticmethod
    async def handle_file_validation(
        file: UploadFile,
    ) -> Either[tuple[str, str], IllegalArgumentError]:

        if file.content_type and not FileValidator.validate_file_type(
            file.content_type
        ):
            return result_fail(
                IllegalArgumentError(
                    None, "Invalid file type. Only JPEG, PNG, and GIF are allowed."
                )
            )

        if file.size is not None and not FileValidator.validate_file_size(file.size):
            return result_fail(
                IllegalArgumentError(
                    None, f"File size exceeds the {MAX_FILE_SIZE} limit"
                )
            )
        else:
            file_size = await FileValidator.stream_file_size(file)

            if is_fail(file_size):
                return result_fail(file_size.value)

        if file.content_type is None:
            return result_fail(
                IllegalArgumentError(None, "File content type is missing.")
            )

        filename = FileValidator.format_filename(file.filename)

        return result_ok((filename, file.content_type))

    @staticmethod
    def format_filename(filename: str | None) -> str:
        if filename is None:
            return UUID().hex

        # Remove special characters and spaces, but keep the file extension if it exists
        formatted = "".join(e for e in filename if e.isalnum() or e == ".").lower()
        return formatted

    @staticmethod
    def validate_content_type(
        file: UploadFile,
    ) -> Either[str, IllegalArgumentError]:
        if file.content_type is None:
            return result_fail(
                IllegalArgumentError(None, "File content type is missing.")
            )

        return result_ok(file.content_type)

    @staticmethod
    def validate_receipt_file(
        file: UploadFile,
    ) -> Either[tuple[str, str], IllegalArgumentError]:
        content_type_result = FileValidator.validate_content_type(file)

        if is_fail(content_type_result):
            return result_fail(content_type_result.value)

        content_type = content_type_result.value

        filename = FileValidator.format_filename(file.filename)

        return result_ok((filename, content_type))
