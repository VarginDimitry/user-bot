from typing import Any, cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient


async def download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
) -> Any:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    user = cast(User, await message.get_sender())

    new_link = await insta_service.get_new_link(message.text)
    await client.send_message(
        entity=message.peer_id,
        message=new_link,
        reply_to=message.reply_to_msg_id if user.is_self else message.id,
        silent=True,
        parse_mode="HTML",
    )

    if user.is_self:
        await message.delete()
    return None
