from enum import StrEnum


class CategoryType(StrEnum):
    """Enumerates supported category values."""

    FOOD = "food"
    RENT = "rent"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"
