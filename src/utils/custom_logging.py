import asyncio
import logging

from aiogram import Bot

from config import Config


class TelegramLoggerHandler(logging.Handler):
    def __init__(
        self,
        config: Config,
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

            for msg_part in self.split_error_message(message):
                await self.bot.send_message(
                    self.config.logger.error_logger_send_to, msg_part
                )
        except Exception:
            self.handleError(record)

    @classmethod
    def split_error_message(cls, message: str) -> list[str]:
        MAX_MESSAGE_SIZE = 4096
        lines = message.split("\n")
        result = [""]

        for line in lines:
            if len(line) > MAX_MESSAGE_SIZE:
                for i in range(0, len(line), MAX_MESSAGE_SIZE):
                    result.append(line[i : i + MAX_MESSAGE_SIZE])
            elif len(line) + len(result[-1]) > MAX_MESSAGE_SIZE:
                result.append(line)
            else:
                result[-1] += line
        return result
