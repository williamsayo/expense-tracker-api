from typing import List
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Enum, String, Uuid, ForeignKey, UniqueConstraint
from shared.infrastructure.db.schema import TimeStampMixin, VersionMixin
from shared.infrastructure.db.base import Base
from shared.domain.types.category_types import CategoryType
from shared.domain.types.currency_types import Currency
from shared.domain.types.user_id import UserId


class Budget(Base, TimeStampMixin, VersionMixin):
    """Represents budget."""

    __tablename__ = "budgets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, type_=Uuid(as_uuid=True)
    )
    start_date: Mapped[date] = mapped_column(
        default=lambda: date.today(), nullable=False
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency), default=Currency.EUR, nullable=False
    )
    end_date: Mapped[date] = mapped_column(
        nullable=False, default=lambda: date.today() + timedelta(days=30)
    )
    allocations: Mapped[List["BudgetAllocation"]] = relationship(
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
    budget = relationship("Budget", back_populates="allocations")

    __table_args__ = (
        UniqueConstraint("category", "budget_id", name="unique_budget_allocation"),
    )

    def __repr__(self) -> str:
        return f"BudgetAllocation (category={self.category!r}, amount={self.amount!r}"


class BudgetSummary(Base, TimeStampMixin):
    """Represents sub-budget."""

    __tablename__ = "budget_summaries"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, type_=Uuid(as_uuid=True)
    )
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency), default=Currency.EUR, nullable=False
    )
    start_date: Mapped[date] = mapped_column(
        default=lambda: date.today(), nullable=False
    )
    end_date: Mapped[date] = mapped_column(
        nullable=False, default=lambda: date.today() + timedelta(days=30)
    )
    allocations: Mapped[List["BudgetAllocationSummary"]] = relationship(
        "BudgetAllocationSummary", back_populates="budget"
    )

    def __repr__(self) -> str:
        return f"BudgetSummary (user_id={self.user_id!r}, currency={self.currency}, start_date={self.start_date!r}, end_date={self.end_date!r})"


class BudgetAllocationSummary(Base, TimeStampMixin):
    """Represents sub-budget."""

    __tablename__ = "budget_allocation_summaries"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    budget_id: Mapped[UUID] = mapped_column(
        ForeignKey("budget_summaries.id"), nullable=False, index=True
    )
    category: Mapped[CategoryType] = mapped_column(Enum(CategoryType), nullable=False)
    budget_amount: Mapped[int]
    spent_amount: Mapped[int]
    budget = relationship("BudgetSummary", back_populates="allocations")

    def __repr__(self) -> str:
        return f"BudgetAllocationSummary (category={self.category!r}, spent_amount={self.spent_amount!r}, budget_amount={self.budget_amount!r})"
