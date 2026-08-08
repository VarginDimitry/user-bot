from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from services.gpt_service import GPTService
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

gpt_router = UpdateRouter()


@gpt_router.on(NewMessage(pattern=r"^/gpt$", outgoing=True, incoming=False))
async def ask_gpt(
    message: Message,
    client: FromDishka[TelegramClient],
    gpt_service: FromDishka[GPTService],
) -> None:
    text = message.text.removeprefix("/gpt").strip()
    if not text:
        return

    answer = await gpt_service.ask(prompt=text) or "No response"
    await client.safe_send_message(
        entity=message.peer_id,
        message=answer,
        reply_to=message.id,
        silent=True,
    )
