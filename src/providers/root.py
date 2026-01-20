import logging
from typing import AsyncIterable

import httpx
from aiofiles.tempfile import TemporaryDirectory
from aiogram import Bot
from coloredlogs import ColoredFormatter
from dishka import from_context, provide, Provider, Scope
from telethon.events.common import EventCommon

from config import Config
from utils.custom_logging import TelegramLoggerHandler
from utils.download_media import DownloadService, TmpDirType


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_config(self) -> Config:
        return Config()

    @provide(scope=Scope.APP)
    def provide_telegram_bot(self, config: Config) -> Bot:
        return Bot(config.logger.bot_token)

    @provide(scope=Scope.APP)
    def provide_logger(self, config: Config, bot: Bot) -> logging.Logger:
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

        if config.logger.enable_telegram:
            telegram_handler = TelegramLoggerHandler(bot=bot, config=config)
            telegram_handler.setLevel(logging.ERROR)
            telegram_handler.setFormatter(formatter)
            logger.addHandler(telegram_handler)

        return logger

    @provide(scope=Scope.APP)
    async def httpx_client(self) -> AsyncIterable[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    async def tmp_dir(self) -> AsyncIterable[TmpDirType]:
        async with TemporaryDirectory() as tempdir:
            yield tempdir

    @provide(scope=Scope.REQUEST)
    def download_service(
        self,
        logger: logging.Logger,
        httpx_client: httpx.AsyncClient,
        tmp_dir: TmpDirType,
    ) -> DownloadService:
        return DownloadService(
            logger=logger, httpx_client=httpx_client, tempdir=tmp_dir
        )
