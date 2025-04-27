from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from services.gpt_service import GPTService


async def ask_gpt(event: NewMessage.Event, gpt_service: FromDishka[GPTService]) -> None:
    message = cast(Message, event.message)
    text = message.text.removeprefix("/gpt").strip()
    if not text:
        return

    answer = await gpt_service.ask(prompt=text) or "No response"
    await message.reply(answer)