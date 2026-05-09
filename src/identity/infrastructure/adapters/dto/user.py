from typing import Optional, Any
from pydantic import EmailStr, BaseModel, Field, field_validator
from shared.infrastructure.adapters.dto.base import BaseReadModel
from identity.domain.value_objects.email_value_object import EmailValueObject


class UserBaseModel(BaseModel):
    """Base model for user data."""

    email: EmailStr = Field(..., examples=["username@example.com"])
    username: str = Field(..., examples=["username"], description="public facing name")
    first_name: str | None = Field(
        None, min_length=2, max_length=50, description="First name of the user"
    )
    last_name: str | None = Field(
        None, min_length=2, max_length=50, description="Last name of the user"
    )


class UserReadModel(BaseReadModel, UserBaseModel):
    """Pydantic model for reading user data, excluding sensitive information like password."""

    created_at: Optional[Any] = Field(
        None, description="Timestamp when the user was created"
    )

    @field_validator("email", mode="before")
    @classmethod
    def parse_email(cls, email) -> str:
        if hasattr(email, "value"):
            return email.value
        return email


class UserWriteModel(UserBaseModel):
    """Write model for user data."""

    password: str = Field(
        ...,
        min_length=1,  # TODO: UPDATE
        description="Password for user login",
        examples=["VerystrongPassword#"],
    )


class UserUpdateModel(BaseModel):
    """Update model for user data."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginModel(BaseModel):
    """Data model for user login."""

    email: str = Field(
        ..., min_length=2, max_length=100, description="Email or username"
    )
    password: str = Field(
        ...,
        min_length=1,  # TODO: UPDATE
        description="Password for user login",
        examples=["VerystrongPassword#"],
    )
