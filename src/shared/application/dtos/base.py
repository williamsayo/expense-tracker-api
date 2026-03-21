from fastapi import Query

class PaginationParams:
    """
    Inject into any route with `params: PaginationParams = Depends()`.
    Supports ?page=1&size=20  OR  ?offset=0&limit=20 (offset takes priority).
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="page number"),
        page_size: int = Query(
            20, ge=1, le=100, description="Items per page (max 100)"
        ),
    ) -> None:
        self.page = page
        self.page_size = page_size
