from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient


async def download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    user = cast(User, await message.get_sender())

    insta_url = message.text.strip()

    media_info = await insta_service.get_media_info_by_link(insta_url)
    text = (
        f"{insta_url}\n\n"
        f"@{media_info.user.username} / <b>{media_info.user.full_name}</b>\n\n"
        f"{media_info.caption_text}"
    )

    await client.send_file(
        entity=message.peer_id,
        file=str(media_info.video_url) or insta_url,
        caption=text[:client.MESSAGE_SIZE_LIMIT],
        reply_to=message.reply_to_msg_id if user.is_self else message.id,
        parse_mode="HTML",
    )

    if user.is_self:
        await message.delete()
