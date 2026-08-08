from typing import Callable

from telethon.events.common import EventBuilder


class UpdateRouter:
    def __init__(self) -> None:
        self.event_handlers: list[tuple[EventBuilder, Callable[..., None]]] = []

    def on(self, event: EventBuilder) -> Callable[[Callable[..., None]], None]:
        def decorator(func: Callable[..., None]) -> None:
            self.event_handlers.append((event, func))

        return decorator

    def include_router(self, router: "UpdateRouter") -> None:
        self.event_handlers.extend(router.event_handlers)
