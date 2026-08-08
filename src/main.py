import asyncio
from logging import Logger
from typing import Awaitable, cast

from dishka import make_async_container

from config import Config
from handlers import get_main_router
from providers.db import DatabaseProvider
from providers.gpt import GPTProvider
from providers.root import RootProvider
from providers.voice_provider import VoiceProvider
from utils.telethon import TelegramClient
from utils.telethon.dishka import setup_dishka, TelethonProvider


async def main() -> None:
    di_container = make_async_container(
        RootProvider(),
        TelethonProvider(),
        DatabaseProvider(),
        VoiceProvider(),
        GPTProvider(),
    )

    config = await di_container.get(Config)
    logger = await di_container.get(Logger)
    client = TelegramClient(
        session=config.user_bot.app_name,
        api_id=config.user_bot.api_id,
        api_hash=config.user_bot.api_hash,
        loop=asyncio.get_running_loop(),
        base_logger=logger,
    )
    setup_dishka(di_container, client)

    client.include_router(get_main_router())
    await cast(Awaitable[None], client.start())
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
