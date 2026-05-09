from pydantic import ConfigDict, BaseModel, Field
from datetime import datetime
from pydantic.alias_generators import to_camel


class BaseReadModel(BaseModel):
    """Read model for base data."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )

    updated_at: datetime | None = Field(default=None, exclude=True)
    created_at: datetime | None = Field(default=None, exclude=True)
