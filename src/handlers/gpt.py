from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from services.gpt_service import GPTService
from utils.custom_telegram_client import MegaTelegramClient


async def ask_gpt(event: NewMessage.Event, gpt_service: FromDishka[GPTService]) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    text = message.text.removeprefix("/gpt").strip()
    if not text:
        return

    answer = await gpt_service.ask(prompt=text) or "No response"
    await client.send_message(
        entity=message.peer_id,
        message=answer,
        reply_to=message.id,
    )
