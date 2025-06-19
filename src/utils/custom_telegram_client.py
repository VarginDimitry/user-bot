from typing import Any, Final, Callable

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection
from telethon import TelegramClient, hints
from telethon.events.common import EventBuilder
from telethon.tl import types


class MegaTelegramClient(TelegramClient):  # type: ignore[misc]
    MESSAGE_SIZE_LIMIT: Final[int] = 4096
    CAPTION_SIZE_LIMIT: Final[int] = 1024
    CAPTION_SIZE_LIMIT_WITH_PREMIUM: Final[int] = 2048

    def __init__(
        self, di_container: AsyncContainer, logger: Any, **kwargs: Any
    ) -> None:
        self.di_container = di_container
        super().__init__(base_logger=logger, **kwargs)

    # func: Callable[..., T]) -> Callable[..., T]
    def add_event_handler(
        self, callback: Callable[..., None], event: EventBuilder = None
    ) -> None:
        di_wrapper = wrap_injection(
            func=callback,
            container_getter=lambda args, kwargs: self.di_container,
            is_async=True,
            manage_scope=True,
        )
        return super().add_event_handler(di_wrapper, event)

    async def safe_send_message(
        self,
        entity: hints.EntityLike,
        message: str = "",
        **kwargs: Any,
    ) -> list[types.Message]:
        messages = split_by_size(message, self.MESSAGE_SIZE_LIMIT)
        return [
            await self.send_message(
                entity,
                m,
                **kwargs,
            )
            for m in messages
        ]


def split_by_size(text: str, max_size: int) -> list[str]:
    return [text[i : i + max_size] for i in range(0, len(text), max_size)]
