from fastapi import Depends
from typing import Self
from dataclasses import dataclass, fields

@dataclass(slots=True, frozen=True)
class BaseDependency:
    """Base class for dependency containers."""

    def list_deps(self):
        return [getattr(self, field.name) for field in fields(self)]

    @classmethod
    def as_dependency(cls) -> Self:
        """Callable for FastAPI dependency injection."""
        return Depends(cls)
