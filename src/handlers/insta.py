from typing import cast

import aiofiles
import httpx
from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient
from utils.download_media import download_media_by_info


async def download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
    httpx_client: FromDishka[httpx.AsyncClient],
) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    user = cast(User, await message.get_sender())

    insta_url = insta_service.process_url(message.text.strip())
    media_info = await insta_service.get_media_info_by_link(insta_url)

    text = (
        f"{insta_url}\n\n"
        f"❤️ {insta_service.beautify_int(media_info.like_count)} / "
        f"💬 {insta_service.beautify_int(media_info.comment_count) if not media_info.comments_disabled else 'comments disabled'}\n\n"
        f"@{media_info.user.username} / <b>{media_info.user.full_name}</b>\n\n"
        f"{media_info.caption_text}"
    )
    async with aiofiles.tempfile.TemporaryDirectory() as tempdir:
        path = await download_media_by_info(
            httpx_client=httpx_client,
            tempdir=tempdir,
            media_info=media_info,
        )

        await client.send_message(
            entity=message.peer_id,
            file=path,
            message=text
            if len(text) < client.CAPTION_SIZE_LIMIT
            else f"{text[: client.CAPTION_SIZE_LIMIT - 3]}...",
            reply_to=message.reply_to_msg_id if user.is_self else message.id,
            silent=True,
            parse_mode="HTML",
        )

    if user.is_self:
        await message.delete()
