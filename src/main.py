import asyncio
from logging import Logger
from typing import Awaitable, cast

from dishka import make_async_container

from config import Config
from handlers import register_handlers
from providers.db import DatabaseProvider
from providers.gpt import GPTProvider
from providers.insta import InstaProvider
from providers.root import RootProvider
from providers.voice_provider import VoiceProvider
from utils.custom_telegram_client import MegaTelegramClient


async def main() -> None:
    di_container = make_async_container(
        RootProvider(),
        DatabaseProvider(),
        VoiceProvider(),
        GPTProvider(),
        InstaProvider(),
    )

    config = await di_container.get(Config)
    logger = await di_container.get(Logger)
    client = MegaTelegramClient(
        session=config.user_bot.app_name,
        api_id=config.user_bot.api_id,
        api_hash=config.user_bot.api_hash,
        loop=asyncio.get_running_loop(),
        di_container=di_container,
        logger=logger,
    )

    register_handlers(client, config)
    await cast(Awaitable[None], client.start())
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
