import re

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from services.gpt_service import GPTService
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

gpt_router = UpdateRouter()


@gpt_router.on(
    NewMessage(pattern=r"(?i)^гпт\b", outgoing=True, incoming=False, forwards=False)
)
async def ask_gpt(
    message: Message,
    user: FromDishka[User],
    client: FromDishka[TelegramClient],
    gpt_service: FromDishka[GPTService],
) -> None:
    text = re.sub(r"(?i)^гпт\s*", "", message.text or "").strip()
    if not text:
        return

    answer = await gpt_service.ask(
        user_id=str(user.id), prompt=text, prompt_message_id=str(message.id)
    )

    messages = await client.safe_send_message(
        entity=message.peer_id,
        message=answer.message,
        reply_to=message.id,
        silent=True,
    )
    if not answer.callback:
        return None

    await answer.callback(messages[0].id)
