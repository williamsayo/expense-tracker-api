from typing import Required, Type, TypedDict
from uuid import UUID
from sqlalchemy import FromClause, select, asc, desc
from boilerplate import GetAllOptions, GetOptions


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

    if offset := options.get("offset"):
        statement = statement.offset(offset)

    if limit := options.get("limit"):
        statement = statement.limit(limit)

    return statement
