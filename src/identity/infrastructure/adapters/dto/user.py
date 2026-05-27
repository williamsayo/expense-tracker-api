from typing import Optional
from fastapi import Form
from datetime import datetime
from pydantic import EmailStr, BaseModel, Field, HttpUrl, field_validator
from src.shared.infrastructure.adapters.dto.base import BaseReadModel


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


class UserAvatarReadModel(BaseModel):
    """Base model for user avatar data."""

    avatar: HttpUrl = Field(
        ...,
        description="URL of the user's avatar",
        examples=["https://example.com/avatar.jpg"],
    )


class UserReadModel(BaseReadModel, UserBaseModel):
    """Pydantic model for reading user data, excluding sensitive information like password."""

    avatar: HttpUrl | None = Field(
        None,
        description="URL of the user's avatar",
        examples=["https://example.com/avatar.jpg"],
    )
    created_at: Optional[datetime] = Field(
        default=None, description="Timestamp when the user was created"
    )

    @field_validator("email", mode="before")
    @classmethod
    def parse_email(cls, email) -> str:
        if hasattr(email, "value"):
            return email.value
        return email

    @field_validator("avatar", mode="before")
    @classmethod
    def parse_avatar(cls, avatar) -> str | None:
        if hasattr(avatar, "url"):
            return avatar.url
        return avatar

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

    @classmethod
    def form(
        cls,
        email: str | None = Form(None),
        username: Optional[str] = Form(None),
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
    ):
        return cls(
            email=email, username=username, first_name=first_name, last_name=last_name
        )


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


class ResetPasswordModel(BaseModel):
    """Write model for user data."""

    old_password: str = Field(
        ...,
        min_length=1,
        description="Current password for user login",
        examples=["VerystrongPassword#"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="New password for user login",
        examples=["password#"],
    )
    confirm_password: str = Field(
        ...,
        description="Confirm new password for user login",
        examples=["password#"],
    )

    @field_validator("confirm_password", mode="before")
    @classmethod
    def validate_passwords_match(cls, confirm_password, info):
        password = info.data.get("password")
        if confirm_password != password:
            raise ValueError("Passwords do not match")
        return confirm_password
