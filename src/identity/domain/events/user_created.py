from typing import TypedDict, Self, cast, Any
from boilerplate import (
    DomainEvent,
    DomainEventInput,
    DomainEventMetadata,
)
from src.shared.domain.types.event_types import EventTypes


class UserCreatedData(TypedDict):
    """Typed dictionary for the data payload of the UserCreated event."""

    user_id: str
    email: str


class UserCreated(DomainEvent[UserCreatedData]):
    """Domain event representing the creation of a new user."""

    def __init__(
        self,
        payload: DomainEventInput[UserCreatedData],
    ):
        super().__init__(payload)

    @classmethod
    def create_event(
        cls, data: UserCreatedData, *, metadata: dict[str, Any] | None = None
    ) -> Self:
        """Factory method to create an instance of UserCreated with the given data and optional metadata."""
        return cls(
            {
                "data": data,
                "metadata": cast(
                    DomainEventMetadata,
                    {**user_created_metadata, **(metadata or {})},
                ),
            }
        )


user_created_metadata: DomainEventMetadata = {
    "type": EventTypes.USER_CREATED.value,
    "description": "Event triggered when a new user is created.",
}
