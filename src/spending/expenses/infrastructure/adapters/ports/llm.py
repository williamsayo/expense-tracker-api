from typing import Protocol
from boilerplate import CoreError
from result import Either


class LLMServiceProtocol(Protocol):

    async def extract_receipt_info(
        self,
        file_url: str,
        *,
        content_type: str = "image/jpeg",
    ) -> Either[dict, CoreError]:
        """Extract structured receipt information from text and image using OpenAI.
        Args:
            file_url: URL of the receipt file.
            content_type: Type of the file (e.g., "image/jpeg").
        Returns:
            Either the extracted receipt information as a dictionary or a CoreError.
        """

        ...
