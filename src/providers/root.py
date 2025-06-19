import logging

import httpx
from dishka import Provider, Scope, from_context, provide
from telethon.events.common import EventCommon

from config import BotSettings


class RootProvider(Provider):
    event = from_context(EventCommon, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> BotSettings:
        return BotSettings()

    @provide(scope=Scope.APP)
    def provide_logger(self, bot_settings: BotSettings) -> logging.Logger:
        logger = logging.getLogger(bot_settings.APP_NAME)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        return logger

    @provide(scope=Scope.APP)
    def httpx_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient()
