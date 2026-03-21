from typing import Type
from sqlalchemy import select, asc, desc
from boilerplate import GetOptions

def build_query[Model](model: Type[Model], options: GetOptions):
    statement = select(model)

    if filter := options.get("filter"):
        statement = statement.filter_by(**filter)

    if projection := options.get("projection"):
        columns = [
            getattr(model, col) for col, include in projection.items() if include
        ]
        statement = statement.with_only_columns(*columns)

    if order_by := options.get("order_by"):
        for col, direction in order_by.items():
            column = getattr(model, col)
            statement = statement.order_by(asc(column) if direction == "asc" else desc(column))

    if limit := options.get("limit"):
        statement = statement.limit(limit)

    if offset := options.get("offset"):
        statement = statement.offset(offset)

    return statement
