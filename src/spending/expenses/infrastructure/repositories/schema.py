from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Text, ForeignKey, String, Index, DateTime
from datetime import datetime, UTC
from sqlalchemy import Uuid, Enum
from shared.infrastructure.db.base import Base
from shared.infrastructure.db.schema import TimeStampMixin, VersionMixin
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency


class Expense(Base, TimeStampMixin, VersionMixin):
    """Represents expense."""

    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    budget_id: Mapped[UUID] = mapped_column(ForeignKey("budgets.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    category: Mapped[CategoryType] = mapped_column(
        Enum(CategoryType), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[Currency] = mapped_column(Enum(Currency), default=Currency.EUR)
    note: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        Index("idx_expenses_user_category", "category", "user_id"),
        Index("idx_expenses_user_category_date", "user_id", "category", "date"),
    )

    def __repr__(self) -> str:
        return f"Expense (category={self.category!r}, amount={self.amount!r}, currency={self.currency!r})"
