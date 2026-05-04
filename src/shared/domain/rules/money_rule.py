from pydantic import BaseModel, Field
from shared.domain.types.currency_types import Currency


class MoneySchema(BaseModel):
    """Validation schema for money."""

    amount: int = Field(..., gt=50)  # Minimum amount of 0.50
    currency: Currency = Field(default=Currency.EUR)  # Minimum amount of 0.50