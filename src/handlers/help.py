from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from config import Config
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

help_router = UpdateRouter()


@help_router.on(NewMessage(pattern=r"(?i)^бот\s+инфо\b", outgoing=True, incoming=False))
async def bot_help(
    message: Message,
    client: FromDishka[TelegramClient],
    config: FromDishka[Config],
) -> None:
    me = await client.get_me()

    text = (
        f"Я ассистент {me.first_name} {me.last_name} (Модель: {config.openai.model})\n"
        f"Мои возможности:\n"
        f"- Транскрибирование голосовых сообщений (Отправь голосовое или ответь «в текст»)\n"
        f"- Вопросы к GPT (гпт <вопрос>)\n"
        f"- Скачать фото/видео из Instagram (Отправь ссылку на instagram)"
    )

    await client.safe_send_message(
        entity=message.peer_id,
        message=text,
        reply_to=message.id,
        silent=True,
    )
