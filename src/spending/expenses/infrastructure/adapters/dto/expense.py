from pydantic import BaseModel, Field, HttpUrl, field_serializer, field_validator
from uuid import UUID
from typing import Self
from datetime import datetime, UTC
from decimal import Decimal
from src.shared.infrastructure.adapters.dto.base import BaseReadModel
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency
from src.spending.expenses.domain.entities.expense_entity import ExpenseEntity
from fastapi import Form


class ExpenseModel(BaseModel):
    """Data model for expense."""

    name: str | None = Field(None, description="Name of the expense")
    merchant: str | None = Field(None, description="Merchant or vendor of the expense")
    note: str | None = Field(
        None,
        description="Note about the expense",
        json_schema_extra={"example": "Dinner with friends"},
    )


class ExpenseReadModel(BaseReadModel):
    """Read model for expense data."""

    id: str | UUID = Field(..., description="ID of the expense")
    user_id: UUID = Field(
        ..., description="ID of the user who made the expense", exclude=True
    )
    name: str | None = Field(None, description="Name of the expense")
    category: Category = Field(..., description="Category of the expense")
    amount: int = Field(..., description="Amount of the expense in cents")
    currency: Currency = Field(..., description="Currency of the expense")
    date: datetime = Field(..., description="Date the expense was made")
    note: str | None = Field(None, description="Note about the expense")
    merchant: str | None = Field(None, description="Merchant or vendor of the expense")
    receipt: HttpUrl | None = Field(None, description="Receipt for the expense")

    @field_serializer("amount")
    def serialize_amount(self, value: int) -> float:
        return value / 100

    @field_validator("receipt", mode="before")
    @classmethod
    def parse_receipt(cls, receipt) -> str | None:
        if hasattr(receipt, "url"):
            return receipt.url
        return receipt

    @classmethod
    def from_entity(cls, entity: ExpenseEntity) -> Self:
        return cls(
            id=entity.id.value,
            user_id=entity.user_id,
            category=entity.category.name,
            amount=entity.money.amount,
            note=entity.note,
            date=entity.date,
            currency=entity.money.currency,
            name=entity.name,
            merchant=entity.merchant,
            receipt=(
                HttpUrl(entity.receipt.url)
                if entity.receipt and entity.receipt.url
                else None
            ),
        )


class ExpenseWriteModel(ExpenseModel):
    """Write model for expense data."""

    category: Category = Field(..., description="Category of the expense")
    date: datetime = Field(
        default=datetime.now(UTC), description="Date the expense was made"
    )
    currency: Currency = Field(default=Currency.EUR)
    amount: Decimal = Field(
        ...,
        decimal_places=2,
        ge=Decimal("0.1"),
        description="amount of the expense in the specified currency",
        examples=[100.00],
    )

    @classmethod
    def form(
        cls,
        date: datetime = Form(
            default=datetime.now(UTC), description="Date the expense was made"
        ),
        category: Category = Form(..., description="Category of the expense"),
        amount: Decimal = Form(
            ...,
            decimal_places=2,
            ge=0.1,
            description="amount of the expense in the specified currency",
            examples=[100.00],
        ),
        currency: Currency = Form(default=Currency.EUR),
        name: str | None = Form(None, description="Name of the expense"),
        merchant: str | None = Form(
            None, description="Merchant or vendor of the expense"
        ),
        note: str | None = Form(
            None,
            description="Note about the expense",
            json_schema_extra={"example": "Dinner with friends"},
        ),
    ):
        return cls(
            date=date,
            category=category,
            amount=amount,
            currency=currency,
            name=name,
            note=note,
            merchant=merchant,
        )


class ExpenseUpdateModel(ExpenseModel):
    """Update model for expense data."""

    date: datetime | None = Field(None, description="Date the expense was made")
    category: Category | None = Field(None, description="Category of the expense")
    amount: Decimal | None = Field(None, decimal_places=2, ge=Decimal("0.1"))
    currency: Currency | None = Field(default=None)

    @classmethod
    def form(
        cls,
        date: datetime | None = Form(None, description="Date the expense was made"),
        category: Category | None = Form(None, description="Category of the expense"),
        amount: Decimal | None = Form(None, decimal_places=2, ge=0.1),
        currency: Currency | None = Form(None),
        name: str | None = Form(None, description="Name of the expense"),
        merchant: str | None = Form(
            None, description="Merchant or vendor of the expense"
        ),
        note: str | None = Form(
            None,
            description="Note about the expense",
            json_schema_extra={"example": "Dinner with friends"},
        ),
    ):
        return cls(
            date=date,
            category=category,
            amount=amount,
            currency=currency,
            name=name,
            note=note,
            merchant=merchant,
        )
