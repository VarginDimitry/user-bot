import logging
from typing import AsyncIterable

import httpx
from aiogram import Bot
from coloredlogs import ColoredFormatter
from dishka import from_context, provide, Provider, Scope
from telethon.events.common import EventCommon

from config import BotSettings
from utils.custom_logging import TelegramLoggerHandler


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> BotSettings:
        return BotSettings()

    @provide(scope=Scope.APP)
    def provide_telegram_bot(self, bot_settings: BotSettings) -> Bot:
        return Bot(bot_settings.TELEGRAM_BOT_TOKEN)

    @provide(scope=Scope.APP)
    def provide_logger(self, bot_settings: BotSettings, bot: Bot) -> logging.Logger:
        logger = logging.getLogger(bot_settings.APP_NAME)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        colored_formatter = ColoredFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

        telegram_handler = TelegramLoggerHandler(bot=bot, config=bot_settings)
        telegram_handler.setLevel(logging.ERROR)
        telegram_handler.setFormatter(formatter)
        logger.addHandler(telegram_handler)

        return logger

    @provide(scope=Scope.APP)
    async def httpx_client(self) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client
