from asyncio import Task, CancelledError, create_task, sleep, get_running_loop
from collections import defaultdict
import logging
from typing import List
from boilerplate import EventHandler, IEventDispatcher, DomainEvent, DomainEventPayload
import functools


class EventDispatcher(IEventDispatcher):
    MAX_RETRY_ATTEMPTS = 3
    BACKOFF_FACTOR = 2

    def __init__(self) -> None:
        self._events: dict[str, DomainEventPayload] = {}
        self._retry_count: dict[str, int] = defaultdict(int)
        self._handlers: dict[str, List[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def dispatch(self, domainEvent: DomainEvent) -> None:
        event = domainEvent.event_dict
        self._register_event(event)
        event_type = event["metadata"]["type"]
        for handler in self._handlers[event_type]:
            self._handle_event(handler, event)

    def _handle_event(self, handler: EventHandler, event: DomainEventPayload) -> None:
        task = create_task(handler.handle(event))
        callback = functools.partial(
            self._task_done_callback, id=event["event_id"], handler=handler
        )
        task.add_done_callback(callback)

    def _task_done_callback(self, task: Task, id: str, handler: EventHandler) -> None:
        try:
            result = task.result()
            logging.info(f"Event handler task completed with result: {result}")
            self._remove_event(id)
        except CancelledError:
            logging.error(f"Event handler task was cancelled.")
            self._remove_event(id)
        except Exception as error:
            logging.error(f"Error in event handler task: {error}")
            # Schedule an async retry with backoff
            try:
                get_running_loop().create_task(self._retry_failed_task(id, handler))
            except RuntimeError:
                create_task(self._retry_failed_task(id, handler))

    async def _retry_failed_task(self, id: str, handler: EventHandler) -> None:
        retry_count = self._retry_count.get(id, 0)

        if retry_count >= self.MAX_RETRY_ATTEMPTS:
            logging.error(f"Max retry attempts reached for event with id {id}.")
            self._remove_event(id)
            return

        backoff = 5 * (self.BACKOFF_FACTOR**retry_count)

        logging.info(
            f"Retrying event {id} after {backoff}s (attempt {retry_count + 1})"
        )
        await sleep(backoff)

        event = self._get_event(id)
        if event is None:
            logging.error(f"Event with id {id} not found for retry.")
            return

        self._retry_count[id] = retry_count + 1
        self._handle_event(handler, event)

    def _register_event(self, event: DomainEventPayload) -> None:
        self._events[event["event_id"]] = event

    def _remove_event(self, event_id: str) -> None:
        self._events.pop(event_id, None)
        self._retry_count.pop(event_id, None)

    def _get_event(self, event_id: str) -> DomainEventPayload | None:
        return self._events.get(event_id, None)

    def _clear_handlers(self) -> None:
        self._handlers.clear()
