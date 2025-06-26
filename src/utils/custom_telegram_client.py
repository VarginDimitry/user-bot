from typing import Any, Callable, Final, Iterable

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection
from telethon import hints, TelegramClient
from telethon.events.common import EventBuilder
from telethon.tl import types

from utils.strings import split_by_size


class SafeTelegramClient(TelegramClient):  # type: ignore[misc]
    MESSAGE_SIZE_LIMIT: Final[int] = 4096
    CAPTION_SIZE_LIMIT: Final[int] = 1024
    CAPTION_SIZE_LIMIT_WITH_PREMIUM: Final[int] = 2048

    def __init__(self, session: str, **kwargs: Any) -> None:
        super().__init__(
            session=session,
            system_version=f"4.16.30-vx{session}",
            **kwargs,
        )

    async def safe_send_message(
        self,
        entity: hints.EntityLike,
        message: str = "",
        style: str | None = None,
        **kwargs: Any,
    ) -> list[types.Message]:
        messages: Iterable[str] = split_by_size(message, self.MESSAGE_SIZE_LIMIT)
        if style:
            messages = (f"<{style}>{m}</{style}>" for m in messages)

        return [
            await self.send_message(
                entity,
                m,
                **kwargs,
            )
            for m in messages
        ]


class MegaTelegramClient(SafeTelegramClient):  # type: ignore[misc]
    def __init__(
        self, di_container: AsyncContainer, logger: Any, **kwargs: Any
    ) -> None:
        self.di_container = di_container
        super().__init__(base_logger=logger, **kwargs)

    def add_event_handler(
        self, callback: Callable[..., None], event: EventBuilder = None
    ) -> None:
        di_wrapper = wrap_injection(
            func=callback,
            container_getter=lambda args, kwargs: self.di_container,
            is_async=True,
            manage_scope=True,
        )
        super().add_event_handler(di_wrapper, event)
