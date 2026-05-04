from collections import defaultdict
from inspect import isawaitable
from typing import List
from boilerplate import EventHandler, IEventBus, DomainEvent


class EventBus(IEventBus):
    def __init__(self) -> None:
        self._handlers: dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = event.payload["metadata"]["type"]
        for handler in self._handlers[event_type]:
            result = handler.handle(event)
            if isawaitable(result):
                await result
