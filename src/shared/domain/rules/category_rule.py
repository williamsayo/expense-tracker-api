from pydantic import BaseModel
from src.shared.domain.types.category_types import Category


class CategorySchema(BaseModel):
    """Validation schema for category."""

    name: Category
