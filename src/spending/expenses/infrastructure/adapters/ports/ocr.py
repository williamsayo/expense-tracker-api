from typing import Protocol
from boilerplate import CoreError
from result import Either

class OCRServiceProtocol(Protocol):

    async def extract_text_from_image(
        self,
        content: bytes,
    ) -> Either[str, CoreError]:
        """Extract text from an image using OCR.
        Args:
            content: The image content as bytes.
        Returns:
            Either the extracted text or a CoreError.
        """
        ...
