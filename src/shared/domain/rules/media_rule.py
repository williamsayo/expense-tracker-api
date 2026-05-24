from pydantic import BaseModel, HttpUrl


class MediaSchema(BaseModel):
    """Validation schema for media."""

    media_key: str | None
    media_url: HttpUrl | None
