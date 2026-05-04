from typing import TypedDict
from dataclasses import dataclass
from enum import StrEnum
from pydantic import BaseModel


class RefreshTokenData(BaseModel):
    """Pydantic model for refresh token data."""
    refresh_token: str

@dataclass
class AccessTokenData:
    """Pydantic model for access token data."""

    access_token: str
    token_type: str = "bearer"


class Token(StrEnum):
    """Enumerates supported token values."""

    ACCESS = "access"
    REFRESH = "refresh"


class RefreshTokenPayload(TypedDict):
    """Typed dictionary for refresh token fields."""

    sub: str
    jti: str


class TokenPayload(TypedDict):
    """Typed dictionary for token fields."""

    sub: str
    token_type: Token
    jti: str
    exp: int | float


@dataclass
class TokenData:
    """Container for token values."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
