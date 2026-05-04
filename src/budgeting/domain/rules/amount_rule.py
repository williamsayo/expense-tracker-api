from pydantic import BaseModel, Field


class AmountSchema(BaseModel):
    """Validation schema for money."""

    amount: int = Field(..., gt=50)
