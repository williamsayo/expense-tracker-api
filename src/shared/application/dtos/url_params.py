from dataclasses import dataclass
from enum import StrEnum
from typing import Optional
from fastapi import Query, Request


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"


@dataclass
class PageParams:
    limit: int
    offset: int
    sort: str
    sort_order: SortOrder


class UrlParams:
    """
    Inject into any route with `params: PaginationParams = Depends()`.
    Supports ?page=1&size=20  OR  ?offset=0&limit=20 (offset takes priority).
    """

    def __init__(
        self,
        request: Request,
        page: int = Query(1, ge=1, description="page number"),
        page_size: int = Query(
            20, ge=1, le=100, description="Items per page (max 100)"
        ),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: Optional[SortOrder] = Query(
            None, description="Sort order: 'asc' or 'desc'"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_order = sort_order
        
        # All extra params not already captured above
        reserved = {"page", "page_size", "sort_by", "sort_order"}
        self.filters: dict = {
            k: v for k, v in request.query_params.items() if k not in reserved
        }
