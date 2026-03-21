from pydantic import BaseModel
from shared.domain.types.category_types import CategoryType


class CategorySchema(BaseModel):
    """Validation schema for category."""
    name: CategoryType
