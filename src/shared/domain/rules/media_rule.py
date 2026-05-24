from pydantic import BaseModel, HttpUrl


class MediaSchema(BaseModel):
    """Validation schema for media."""

    key: str | None
    url: HttpUrl | None
