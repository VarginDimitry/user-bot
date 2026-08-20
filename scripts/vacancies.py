import asyncio
import json
from datetime import datetime, timezone, timedelta
from logging import Logger
import os
from typing import Awaitable, cast

from dishka import make_async_container

from config import Config
from providers.db import DatabaseProvider
from providers.gpt import GPTProvider
from providers.insta import InstaProvider
from providers.root import RootProvider
from providers.voice_provider import VoiceProvider
from utils.telethon import TelegramClient
from utils.telethon.dishka import setup_dishka

CHANNELS: int = [
    {"id": -1001627075588, "name": "Python Jobs | Работа | Вакансии | Удалёнка | [IT MATCH]", "link": "https://web.telegram.org/a/#-1001627075588"},
    {"id": -1001102268569, "name": "Вакансии Backend/Frontend", "link": "https://web.telegram.org/a/#-1001102268569"},
]


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
    
    session = f"/Users/dmitryvargin/IT/PycharmProjects/Pets/user-bot/src/{config.user_bot.app_name}"
    if not os.path.exists(f"{session}.session"):
        raise FileNotFoundError(f"Session file not found: {session}")
    else:
        logger.info(f"Session file found")
    
    client = TelegramClient(
        session=session,
        api_id=config.user_bot.api_id,
        api_hash=config.user_bot.api_hash,
        loop=asyncio.get_running_loop(),
        di_container=di_container,
        logger=logger,
    )
    setup_dishka(di_container, client)

    await cast(Awaitable[None], client.start())

    one_month_ago = datetime.now(tz=timezone.utc) - timedelta(days=31*3)

    data = {}
    for channel in CHANNELS:
        logger.info(f"\nStart processing channel: {channel['name']}")
        channel_id = channel['id']
        data[channel_id] = []
        async for message in client.iter_messages(channel_id):
            if message.date < one_month_ago:
                break
            if (
                not message.text or
                'python' not in message.text.lower()
            ):
                continue
            data[channel_id].append(message.text)
        logger.info(f"Finished processing channel: {channel['name']}")

    with open("data.json", "w") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))

    await di_container.close()


if __name__ == "__main__":
    asyncio.run(main())
