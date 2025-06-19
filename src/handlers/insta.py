import asyncio
from typing import cast

import httpx
from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from dto.instagram import MediaType
from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient


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
        # f"👀 {insta_service.beautify_int(media_info.view_count)} / "
        f"❤️ {insta_service.beautify_int(media_info.like_count)} / "
        f"✍️ {insta_service.beautify_int(media_info.comment_count) if not media_info.comments_disabled else 'comments_disabled'}\n\n"
        f"@{media_info.user.username} / <b>{media_info.user.full_name}</b>\n\n"
        f"{media_info.caption_text}"
    )

    file = media_info.extract_media_urls()
    if not file:
        await client.send_message(
            entity=message.peer_id,
            message="Unsupported media type",
            reply_to=message.reply_to_msg_id if user.is_self else message.id,
            silent=True,
            parse_mode="HTML",
        )
        return

    if len(file) > 1:
        file = [
            response.content
            for response in
            await asyncio.gather(*[
                httpx_client.get(url) for url in file
            ])
        ]

    await client.send_message(
        entity=message.peer_id,
        file=file if media_info.media_type == MediaType.ALBUM else file[0],
        message=text[: client.CAPTION_SIZE_LIMIT],
        reply_to=message.reply_to_msg_id if user.is_self else message.id,
        silent=True,
        parse_mode="HTML",
    )


    if user.is_self:
        await message.delete()
