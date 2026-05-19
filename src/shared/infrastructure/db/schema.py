from datetime import datetime, UTC
from sqlalchemy.orm import declared_attr, mapped_column, Mapped
from sqlalchemy import DateTime, Integer


class VersionMixin:
    """Mixin that adds version fields."""

    version: Mapped[int]

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"version_id_col": cls.version}


class TimeStampMixin:
    """Mixin that adds time stamp fields."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
