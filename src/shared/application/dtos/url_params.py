from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
from fastapi import Query, Request


class SortBy(StrEnum):
    amount = "amount"
    currency = "currency"
    date = "date"


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"


class UrlParams:
    """
    Inject into any route with `params: PaginationParams = Depends()`.
    Supports ?page=1&size=20  OR  ?offset=0&limit=20 (offset takes priority).
    """

    def __init__(
        self,
        request: Request,
        q: Optional[str] = Query(None, description="Search query"),
        page: int = Query(1, ge=1, description="page number"),
        page_size: int = Query(
            20, ge=1, le=100, description="Items per page (max 100)"
        ),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: SortOrder = Query(
            SortOrder.asc, description="Sort order: 'asc' or 'desc'"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.q = q

        # All extra params not already captured above
        reserved = {"page", "page_size", "sort_by", "sort_order", "q"}
        self.filters: dict = {
            key: value
            for key, value in request.query_params.items()
            if key not in reserved
        }
