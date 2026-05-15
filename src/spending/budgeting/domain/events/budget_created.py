from typing import TypedDict, Self, cast, Any
from uuid import UUID
from boilerplate import (
    DomainEvent,
    DomainEventPayload,
    DomainEventMetadata,
)
from datetime import date
from src.shared.domain.types.currency_types import Currency


class BudgetCreatedData(TypedDict):
    """Typed dictionary for the data payload of the BudgetCreated event."""

    name: str | None
    auth_id: str
    budget_id: str
    currency: Currency
    start_date: date
    end_date: date
    allocations: Any


class BudgetCreated(DomainEvent[BudgetCreatedData]):
    """Domain event representing the creation of a new budget."""

    def __init__(
        self,
        payload: DomainEventPayload[BudgetCreatedData],
    ):
        super().__init__(payload)

    @classmethod
    def create_event(
        cls, data: BudgetCreatedData, *, metadata: dict[str, Any] | None = None
    ) -> Self:
        """Factory method to create an instance of BudgetCreated with the given data and optional metadata."""
        return cls(
            {
                "data": data,
                "metadata": cast(
                    DomainEventMetadata,
                    {**budget_created_metadata, **(metadata or {})},
                ),
            }
        )


budget_created_metadata: DomainEventMetadata = {
    "type": BudgetCreated.__name__,
    "description": "Event triggered when a new budget is created.",
}
