import asyncio
import logging
import sys
from types import MethodType
from typing import Awaitable, cast

from dishka import make_async_container, AsyncContainer
from dishka.integrations.base import wrap_injection
from telethon import TelegramClient

from config import BotSettings
from handlers import register_handlers
from providers.root import RootProvider
from providers.voice_provider import VoiceProvider


def setup_dishka_telethon(client: TelegramClient, container: AsyncContainer):
    client.di_container = container
    orig_add_handler = client.add_event_handler

    def add_handler_with_injection(self, callback, event=None):
        di_wrapper = wrap_injection(
            func=callback,
            container_getter=lambda args, kwargs: self.di_container,
            is_async=True,
            manage_scope=True
        )
        return orig_add_handler(di_wrapper, event)

    client.add_event_handler = MethodType(add_handler_with_injection, client)


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    bot_settings = BotSettings()  # type: ignore
    client = TelegramClient(
        session="Telethon",
        api_id=bot_settings.API_ID,
        api_hash=bot_settings.API_HASH,
        loop=asyncio.get_running_loop(),
    )

    container = make_async_container(
        RootProvider(),
        VoiceProvider(),
    )
    setup_dishka_telethon(client, container)

    register_handlers(client)
    await cast(Awaitable, client.start())
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
