from typing import TypedDict
from enum import StrEnum


class Token(StrEnum):
    """Enumerates supported token values."""

    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(TypedDict):
    """Typed dictionary for token fields."""

    sub: str
    token_type: Token
    jti: str
    exp: int | float
