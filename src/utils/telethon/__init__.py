from typing import Any

from telethon import TelegramClient

from utils.telethon.router import UpdateRouter
from utils.telethon.safe_message import SafeMessageMixin


class TelegramClient(SafeMessageMixin, TelegramClient):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if args:
            raise ValueError("Arguments are not allowed")

        session = kwargs.pop("session")
        super().__init__(
            session=session,
            system_version=f"4.16.30-vx{session}",
            **kwargs,
        )

    def include_router(self, router: UpdateRouter) -> None:
        for event, handler in router.event_handlers:
            self.add_event_handler(handler, event)
