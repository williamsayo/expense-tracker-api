from openai import AsyncOpenAI
import json
from boilerplate import CoreError
from result import Either, result_fail, result_ok
from src.core.config import get_settings

settings = get_settings()


class OpenAiServiceError(CoreError):
    def __init__(
        self,
        cause: Exception | None = None,
        message: str = "Unexpected error in OpenAI service",
    ):
        super().__init__(cause, message, "openai_service_error")


def openai_parse_receipt_prompt() -> str:
    return f"""
    Extract receipt information.

    IMPORTANT:
    - Use the FINAL total amount paid
    - Ignore subtotal
    - Ignore tax unless tax is final total
    - Merchant should be business/store name
    - Normalize date to YYYY-MM-DD
    - Category should be one of: Food, Transportation, Entertainment, Utilities, Healthcare, Other
    - Detect currency symbol/code
    - Name the expense based on merchant and category, e.g. "Starbucks Coffee" for a food purchase at Starbucks
    - Note should be any additional info you can extract, e.g. "2x Latte, 1x Croissant" for a Starbucks receipt
    - If you cannot find a field, return null for that field
    - Name the fields exactly as specified: total_amount, currency, date, merchant, name , category, note

    Return JSON only.
    """


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())

    async def extract_receipt_info(
        self,
        image: str,
        *,
        is_image: bool = True,
        is_url: bool = False,
    ) -> Either[dict, OpenAiServiceError]:
        """Extract structured receipt information from text and image using OpenAI.
        Args:
            image: Optional base64-encoded image of the receipt.
            image_url: Optional URL of the receipt image."""

        content = f"data:image/jpeg;base64,{image}" if is_image else image

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You extract receipt data. Return ONLY valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": openai_parse_receipt_prompt(),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": content},
                            },
                        ],
                    },
                ],
                temperature=0,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content

            if content is None:
                return result_fail(
                    OpenAiServiceError(
                        None,
                        "Failed to extract receipt info from OpenAI",
                    )
                )

            return result_ok(json.loads(content))

        except Exception as error:
            return result_fail(
                OpenAiServiceError(error, "Failed to extract receipt info from OpenAI")
            )
