from pydantic import BaseModel, Field
from decimal import Decimal


class MoneySchema(BaseModel):
    """Validation schema for money."""

    amount: int = Field(..., gt=50)  # Minimum amount of 0.50
    currency: str = Field(..., min_length=3, max_length=3)
