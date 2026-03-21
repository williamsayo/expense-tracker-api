from typing import TypedDict
from dataclasses import dataclass
from enum import StrEnum


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
