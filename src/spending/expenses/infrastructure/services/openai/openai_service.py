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
        message: str = "Unexpected error in LLM service",
    ):
        super().__init__(cause, message, "llm_service_error")


def openai_parse_receipt_prompt() -> str:
    return f"""
    Extract receipt information.

    IMPORTANT:
    - Use the FINAL total amount paid
    - Ignore subtotal
    - Ignore tax unless tax is final total
    - Merchant should be business/store name
    - Date cannot be null or empty. Default to today's date. Normalize date to YYYY-MM-DD, Default to today's date if you cannot detect it must be in YYYY-MM-DD format
    - Category should be one of: food, rent, transportation, entertainment, utilities, healthcare, other and should be based on merchant and items purchased and not just the merchant alone, e.g. if the receipt is from Amazon but it's for groceries, category should be Food not Other, it should be lowercase and should be one of the specified categories, if you cannot detect category, default to Other
    - Detect currency symbol/code and return as 3-letter code, e.g. USD, EUR, GBP,Default to EUR if you cannot detect
    - Name the expense based on merchant and category, e.g. "Starbucks Coffee" for a food purchase at Starbucks
    - Note should be any additional info you can extract, e.g. "2x Latte, 1x Croissant" for a Starbucks receipt, the note should be a concise summary of the items purchased and any other relevant info, it should not include info that is already captured in other fields like total_amount, date, merchant, category etc.
    - Return null for any field you cannot detect except for category, currency and date which should default to "other", "EUR" and today's date respectively if you cannot detect
    - Name the fields exactly as specified: total_amount, currency, date, merchant, name , category, note

    Return JSON only.
    """


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            base_url="https://api.groq.com/openai/v1",
        )

    async def extract_receipt_info(
        self,
        file_url: str,
        *,
        content_type: str = "image/jpeg",
    ) -> Either[dict, OpenAiServiceError]:
        """Extract structured receipt information from text and image using OpenAI.
        Args:
            image: Optional base64-encoded image of the receipt."""

        try:
            response = await self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
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
                                "image_url": {"url": file_url},
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
                        "Failed to extract receipt info from image: No content returned",
                    )
                )

            return result_ok(json.loads(content))

        except Exception as error:
            return result_fail(
                OpenAiServiceError(error, "Failed to extract receipt info from image")
            )
