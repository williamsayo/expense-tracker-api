class BaseService[T]:
    """Coordinates base application workflows."""

    def __init__(self, deps: T):
        self.deps = deps


class CommandService[T]:
    """Base class for command services."""

    def __init__(self, commandDeps: T):
        self.deps = commandDeps


class QueryService[T]:
    """Base class for query services."""

    def __init__(self, queryDeps: T):
        self.deps = queryDeps
