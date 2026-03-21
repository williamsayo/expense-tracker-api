from fastapi import Depends


class BaseService[T]:
    """Coordinates base application workflows."""

    def __init__(self, deps: T = Depends()):
        self.deps = deps
