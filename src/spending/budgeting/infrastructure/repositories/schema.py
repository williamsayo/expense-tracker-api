from typing import List, TypedDict, NotRequired
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Enum, String, Uuid, ForeignKey, UniqueConstraint
from src.shared.infrastructure.db.schema import TimeStampMixin, VersionMixin
from src.shared.infrastructure.db.base import Base
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency
from src.spending.expenses.infrastructure.repositories.schema import (
    Expense,
    ExpenseSchema,
)

class BudgetSchema(TypedDict):
    id: UUID
    name: str | None
    user_id: UUID
    start_date: date
    end_date: date
    currency: Currency
    allocations: NotRequired[List["BudgetAllocationSchema"]]
    expenses: NotRequired[List[ExpenseSchema]]


class BudgetAllocationSchema(TypedDict):
    id: UUID
    budget_id: UUID
    category: Category
    amount: int
    spent_amount: int


class Budget(Base, TimeStampMixin, VersionMixin):
    """Represents budget."""

    __tablename__ = "budgets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
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
    expenses: Mapped[List["Expense"]] = relationship("Expense")

    __table_args__ = (UniqueConstraint("user_id", "start_date", name="unique_budget"),)

    def __repr__(self) -> str:
        return f"Budget (user={self.user_id!r})"


class BudgetAllocation(Base, TimeStampMixin, VersionMixin):
    """Represents sub-budget."""

    __tablename__ = "budget_allocations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    budget_id: Mapped[UUID] = mapped_column(
        ForeignKey("budgets.id"), nullable=False, index=True
    )
    category: Mapped[Category] = mapped_column(Enum(Category), nullable=False)
    amount: Mapped[int]
    spent_amount: Mapped[int] = mapped_column(default=0, nullable=False)
    budget = relationship("Budget", back_populates="allocations")

    __table_args__ = (
        UniqueConstraint("category", "budget_id", name="unique_budget_allocation"),
    )

    def __repr__(self) -> str:
        return f"BudgetAllocation (category={self.category!r}, amount={self.amount!r}"
