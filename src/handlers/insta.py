from typing import cast

from aiofiles.tempfile import TemporaryDirectory
from dishka import FromDishka
from httpx import AsyncClient
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from dto.instagram import MyMedia
from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient
from utils.download_media import download_media_by_info
from utils.strings import beautify_int


async def download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
    httpx_client: FromDishka[AsyncClient],
) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    user = cast(User, await message.get_sender())

    insta_url = insta_service.process_url(message.text.strip())

    media_info = await insta_service.get_media_info_by_link(insta_url)
    if not media_info:
        await client.send_message(
            entity=message.peer_id,
            message="Can't download media",
            reply_to=message.id,
            silent=True,
            parse_mode="HTML",
        )
        return None

    text = _build_answer_text(insta_url, media_info, client.CAPTION_SIZE_LIMIT)
    async with TemporaryDirectory() as tempdir:
        path = await download_media_by_info(
            httpx_client=httpx_client,
            tempdir=tempdir,
            media_info=media_info,
        )

        await client.send_message(
            entity=message.peer_id,
            file=path,
            message=text,
            reply_to=message.reply_to_msg_id if user.is_self else message.id,
            silent=True,
            parse_mode="HTML",
        )

    if user.is_self:
        await message.delete()
    return None


def _build_answer_text(url: str, media_info: MyMedia, max_size: int = 0) -> str:
    text = (
        f"{url}\n"
        f"❤️ {beautify_int(media_info.like_count)} / "
        f"💬 {beautify_int(media_info.comment_count) if not media_info.comments_disabled else 'comments disabled'}\n"
        f"@{media_info.user.username} / <b>{media_info.user.full_name}</b>\n\n"
        f"{media_info.caption_text}"
    )
    if max_size > 0:
        text = text if len(text) < max_size else f"{text[: max_size - 3]}..."
    return text
