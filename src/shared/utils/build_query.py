from typing import Required, Type, TypedDict
from uuid import UUID
from sqlalchemy import FromClause, select, asc, desc
from boilerplate import GetAllOptions, GetOptions
from src.core.config import get_settings

settings = get_settings()


class AppFilter(TypedDict, total=False):
    user_id: Required[UUID]
    category: str
    # Add more filter fields as needed


def build_query[Model](
    model: Type[Model] | FromClause,
    options: GetAllOptions[AppFilter] | GetOptions[AppFilter],
):
    model_columns = model.columns if isinstance(model, FromClause) else model

    if projection := options.get("select"):
        statement = select(*(getattr(model_columns, col) for col in projection))
    else:
        statement = select(model)

    if filter := options.get("filter"):
        q = filter.pop(
            "q", None
        )  # Remove 'q' from filter as it's used for search, not direct filtering
        statement = statement.filter_by(**filter)

    if sort := options.get("sort"):
        sort_options = []

        for col, direction in sort.items():
            column = getattr(model_columns, col)
            if direction == "asc":
                sort_options.append(asc(column))
            else:
                sort_options.append(desc(column))

        statement = statement.order_by(*sort_options)

    if page := options.get("offset"):
        page_size = options.get("limit", 10)
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)

    return statement
