from pydantic import BaseModel, AnyHttpUrl, field_validator

class MediaSchema(BaseModel):
    """Validation schema for media."""

    media_key: str | None
    media_url: str | None

    @field_validator("media_url", mode="before")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return value

        url = AnyHttpUrl(value)
        return str(url)
