import asyncio
import logging
import sys
from types import MethodType
from typing import Any, Awaitable, Callable, cast

from dishka import AsyncContainer, make_async_container
from dishka.integrations.base import wrap_injection
from telethon.events.common import EventBuilder

from config import BotSettings
from handlers import register_handlers
from providers.gpt import GPTProvider
from providers.insta import InstaProvider
from providers.root import RootProvider
from providers.voice_provider import VoiceProvider
from utils.custom_telegram_client import MegaTelegramClient


async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    di_container = make_async_container(
        RootProvider(),
        VoiceProvider(),
        GPTProvider(),
        InstaProvider(),
    )

    bot_settings = BotSettings()
    client = MegaTelegramClient(
        session="Telethon",
        api_id=bot_settings.API_ID,
        api_hash=bot_settings.API_HASH,
        loop=asyncio.get_running_loop(),
        di_container=di_container,
    )

    register_handlers(client)
    await cast(Awaitable[None], client.start())
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
