from datetime import datetime, UTC
from sqlalchemy.orm import mapped_column, Mapped


class VersionMixin:
    """Mixin that adds version fields."""
    version: Mapped[int]


class TimeStampMixin:
    """Mixin that adds time stamp fields."""

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
