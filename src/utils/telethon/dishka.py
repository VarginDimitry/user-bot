from collections.abc import Callable
from typing import cast

from dishka import AsyncContainer, from_context, provide, Provider, Scope
from dishka.integrations.base import wrap_injection
from telethon.events.common import EventBuilder, EventCommon
from telethon.tl.types import User

from utils.telethon import TelegramClient


class TelethonProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    def provide_client(self, event: EventCommon) -> TelegramClient:
        return cast(TelegramClient, event.client)

    # Message is provided by Telethon itself
    # @provide(scope=Scope.REQUEST)
    # def provide_message(self, event: EventCommon) -> Message:
    #     return cast(Message, cast(Any, event).message)

    @provide(scope=Scope.REQUEST)
    async def provide_user(self, event: EventCommon) -> User:
        return await event.message.get_sender()


def setup_dishka(container: AsyncContainer, client: TelegramClient) -> None:
    client.di_container = container
    original_add_event_handler = client.add_event_handler

    def add_event_handler(
        callback: Callable[..., None], event: EventBuilder | None = None
    ) -> None:
        di_wrapper = wrap_injection(
            func=callback,
            container_getter=lambda args, kwargs: client.di_container,
            is_async=True,
            manage_scope=True,
            provide_context=lambda args, kwargs: {EventCommon: args[0]},
        )
        original_add_event_handler(di_wrapper, event)

    client.add_event_handler = add_event_handler
