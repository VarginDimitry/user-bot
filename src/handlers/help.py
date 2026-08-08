from dishka import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.events import NewMessage
from telethon.tl.patched import Message

from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

help_router = UpdateRouter()


@help_router.on(NewMessage(pattern=r"^/help$", outgoing=True, incoming=False))
async def bot_help(
    message: Message, client: FromDishka[TelegramClient], _: FromDishka[AsyncSession]
) -> None:
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
