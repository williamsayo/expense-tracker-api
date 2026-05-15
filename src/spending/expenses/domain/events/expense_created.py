from typing import TypedDict, Self, cast, Any
from uuid import UUID
from boilerplate import (
    DomainEvent,
    DomainEventPayload,
    DomainEventMetadata,
)
from datetime import datetime
from src.shared.domain.types.category_types import CategoryType
from src.shared.domain.types.currency_types import Currency

class ExpenseCreatedData(TypedDict):
    """Typed dictionary for the data payload of the ExpenseCreated event."""

    auth_id: str | UUID
    expense_id: str | UUID
    category: CategoryType
    amount: int
    currency: Currency
    date: datetime


class ExpenseCreated(DomainEvent[ExpenseCreatedData]):
    """Domain event representing the creation of a new expense."""

    def __init__(
        self,
        payload: DomainEventPayload[ExpenseCreatedData],
    ):
        super().__init__(payload)

    @classmethod
    def create_event(
        cls, data: ExpenseCreatedData, *, metadata: dict[str, Any] | None = None
    ) -> Self:
        """Factory method to create an instance of ExpenseCreated with the given data and optional metadata."""
        return cls(
            {
                "data": data,
                "metadata": cast(
                    DomainEventMetadata,
                    {**expense_created_metadata, **(metadata or {})},
                ),
            }
        )

expense_created_metadata: DomainEventMetadata = {
    "type": ExpenseCreated.__name__,
    "description": "Event triggered when a new expense is created.",
}
