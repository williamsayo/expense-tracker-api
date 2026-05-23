from functools import lru_cache
from .event_dispatcher import EventDispatcher, EventHandler
from src.shared.domain.types.event_types import EventTypes


@lru_cache(maxsize=1)
def get_event_dispatcher() -> EventDispatcher:
    event_dispatcher = EventDispatcher()
    return event_dispatcher


def register_handler(event_type: str, handler: EventHandler) -> None:
    get_event_dispatcher().subscribe(event_type, handler)


def register_handlers(handlers: list[tuple[EventTypes, EventHandler]]) -> None:
    for event_type, handler in handlers:
        register_handler(event_type, handler)
