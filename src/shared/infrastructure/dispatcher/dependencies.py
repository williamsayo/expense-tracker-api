from typing import Generator
from shared.infrastructure.dispatcher.event_bus import EventBus, EventHandler

event_bus = EventBus()

def get_event_bus() -> Generator[EventBus]:
    yield event_bus

def register_handler(event_type: str, handler: EventHandler) -> None:
    event_bus.subscribe(event_type, handler)