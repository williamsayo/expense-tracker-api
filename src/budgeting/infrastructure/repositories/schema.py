from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Enum, Uuid, ForeignKey, UniqueConstraint
from shared.infrastructure.db.schema import TimeStampMixin, VersionMixin
from shared.infrastructure.db.base import Base
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from shared.domain.types.user_id import UserId

class Budget(Base, TimeStampMixin, VersionMixin):
    """Represents budget."""

    __tablename__ = "budgets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, type_=Uuid(as_uuid=True)
    )
    start_date: Mapped[date] = mapped_column(
        default=lambda: date.today(), nullable=False
    )

    end_date: Mapped[date] = mapped_column(
        nullable=False, default=lambda: date.today() + timedelta(days=30)
    )
    allocations: Mapped[list["BudgetAllocation"]] = relationship(
        "BudgetAllocation", back_populates="budget", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("user_id", "start_date", name="unique_budget"),)

    def __repr__(self) -> str:
        return f"Budget (user={self.user_id!r})"


class BudgetAllocation(Base, TimeStampMixin, VersionMixin):
    """Represents sub-budget."""

    __tablename__ = "budget_allocations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    budget_id: Mapped[UUID] = mapped_column(
        ForeignKey("budgets.id"), nullable=False, index=True
    )
    category: Mapped[CategoryType] = mapped_column(Enum(CategoryType), nullable=False)
    amount: Mapped[int]
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency), default=Currency.EUR, nullable=False
    )
    budget = relationship("Budget", back_populates="allocations")

    __table_args__ = (
        UniqueConstraint("category", "budget_id", name="unique_budget_allocation"),
    )

    def __repr__(self) -> str:
        return f"BudgetAllocation (category={self.category!r}, amount={self.amount!r}, currency={self.currency!r})"
