from fastapi import UploadFile
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileUploadDTO:
    file: UploadFile
    filename: str
    content_type: str
    size: int
    original_filename: str | None = None
