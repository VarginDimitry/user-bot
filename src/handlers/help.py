from typing import cast

from dishka import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.events import NewMessage
from telethon.tl.patched import Message

from utils.custom_telegram_client import MegaTelegramClient


async def bot_help(event: NewMessage.Event, _: FromDishka[AsyncSession]) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    me = await client.get_me()

    text = (
        f"Я ассистент {me.first_name} {me.last_name},\n"
        f"Мои возможности:\n"
        f"- Транскрибирование голосовых сообщений (Отправь голосовое сообщение или /transcribe )\n"
        f"- Вопросы к GPT ( /gpt )\n"
        f"- Скачать фото/видео из Instagram (Отправь ссылку на instagram)"
    )

    await client.safe_send_message(
        entity=message.peer_id,
        message=text,
        reply_to=message.id,
        silent=True,
    )
