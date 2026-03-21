from pydantic import BaseModel, EmailStr


class EmailSchema(BaseModel):
    """Validation schema for email."""

    value: EmailStr
