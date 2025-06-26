import asyncio
import logging

from aiogram import Bot

from config import BotSettings


class TelegramLoggerHandler(logging.Handler):
    def __init__(
        self,
        config: BotSettings,
        bot: Bot,
    ) -> None:
        self.config = config
        self.bot = bot
        self.recipient: int | None = None
        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        loop = asyncio.get_running_loop()
        loop.create_task(self.aemit(record))

    async def aemit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            await self.bot.send_message(self.config.SEND_TO, message)
        except Exception:
            self.handleError(record)
