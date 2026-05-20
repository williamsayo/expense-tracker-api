from typing import Protocol
from boilerplate import CoreError
from result import Either


class LLMServiceProtocol(Protocol):

    async def extract_receipt_info(
        self,
        image: str,
        *,
        is_image: bool = True,
        is_url: bool = False,
    ) -> Either[dict, CoreError]:
        """Extract structured receipt information from text and image using OpenAI.
        Args:
            image: Optional base64-encoded image of the receipt or URL of the receipt image.
            is_image: Flag indicating if the provided image is a base64-encoded string.
            is_url: Flag indicating if the provided image is a URL.
        Returns:
            Either the extracted receipt information as a dictionary or a CoreError.
        """

        ...
