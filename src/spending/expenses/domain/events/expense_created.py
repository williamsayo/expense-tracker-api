from typing import TypedDict, Self, cast, Any
from boilerplate import (
    DomainEvent,
    DomainEventInput,
    DomainEventMetadata,
)
from datetime import datetime
from src.shared.domain.types.category_types import Category
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.types.event_types import EventTypes


class ExpenseCreatedData(TypedDict):
    """Typed dictionary for the data payload of the ExpenseCreated event."""

    user_id: str
    name: str | None
    merchant: str | None
    expense_id: str
    category: str
    amount: int
    currency: str
    date: str


class ExpenseCreated(DomainEvent[ExpenseCreatedData]):
    """Domain event representing the creation of a new expense."""

    def __init__(
        self,
        payload: DomainEventInput[ExpenseCreatedData],
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
    "type": EventTypes.EXPENSE_CREATED.value,
    "description": "Event triggered when a new expense is created.",
}
