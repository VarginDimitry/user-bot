import logging
from typing import AsyncIterable

import httpx
from aiogram import Bot
from coloredlogs import ColoredFormatter
from dishka import from_context, provide, Provider, Scope
from telethon.events.common import EventCommon

from config import RootConfig
from utils.custom_logging import TelegramLoggerHandler


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_config(self) -> RootConfig:
        return RootConfig()

    @provide(scope=Scope.APP)
    def provide_telegram_bot(self, config: RootConfig) -> Bot:
        return Bot(config.logger.bot_token)

    @provide(scope=Scope.APP)
    def provide_logger(self, config: RootConfig, bot: Bot) -> logging.Logger:
        logger = logging.getLogger(config.user_bot.app_name)
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

        telegram_handler = TelegramLoggerHandler(bot=bot, config=config)
        telegram_handler.setLevel(logging.ERROR)
        telegram_handler.setFormatter(formatter)
        logger.addHandler(telegram_handler)

        return logger

    @provide(scope=Scope.APP)
    async def httpx_client(self) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client
