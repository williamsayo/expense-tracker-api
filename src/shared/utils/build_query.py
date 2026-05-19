from typing import Type
from sqlalchemy import select, asc, desc
from boilerplate import GetAllOptions


def build_query[Model](model: Type[Model], options: GetAllOptions):
    if projection := options.get("select"):
        statement = select(*(getattr(model, col) for col in projection))
    else:
        statement = select(model)

    if filter := options.get("filter"):
        statement = statement.filter_by(**filter)

    if sort := options.get("sort"):
        sort_options = []

        for col, direction in sort.items():
            column = getattr(model, col)
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
