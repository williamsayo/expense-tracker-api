from typing import TypedDict, Self, cast, Any
from boilerplate import (
    DomainEvent,
    DomainEventInput,
    DomainEventMetadata,
)
from datetime import date
from src.shared.domain.types.currency_types import Currency
from src.shared.domain.types.event_types import EventTypes


class AllocationData(TypedDict):
    """Typed dictionary for the data of each budget allocation in the BudgetCreated event."""

    allocation_id: str
    category: str
    budget_amount: int


class BudgetCreatedData(TypedDict):
    """Typed dictionary for the data payload of the BudgetCreated event."""

    name: str | None
    user_id: str
    budget_id: str
    currency: Currency
    start_date: date
    end_date: date
    allocations: list[AllocationData]


class BudgetCreated(DomainEvent[BudgetCreatedData]):
    """Domain event representing the creation of a new budget."""

    def __init__(
        self,
        payload: DomainEventInput[BudgetCreatedData],
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
    "type": EventTypes.BUDGET_CREATED.value,
    "description": "Event triggered when a new budget is created.",
}
