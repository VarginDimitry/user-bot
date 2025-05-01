from typing import cast

import aiofiles
from dishka import FromDishka
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from services.insta_service import InstaService


async def download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
) -> None:
    message = cast(Message, event.message)
    client = cast(TelegramClient, event.client)
    insta_url = message.text.strip()

    media_info = await insta_service.get_media_info_by_link(insta_url)
    await client.send_file(
        entity=message.chat_id,
        file=str(media_info.video_url) or insta_url,
        caption=insta_url,
    )
    if cast(User, await message.get_sender()).is_self:
        await message.delete()


async def __download_insta(
    event: NewMessage.Event,
    insta_service: FromDishka[InstaService],
) -> None:
    message = cast(Message, event.message)
    client = cast(TelegramClient, event.client)
    sender = cast(User, message.sender)

    async with aiofiles.tempfile.NamedTemporaryFile(suffix=".mp4") as video_file:
        await insta_service.download(message.text.strip(), video_file)
        if sender.is_self:
            await message.delete()
            await client.send_file(
                message.chat_id,
                caption=message.text,
                file=video_file.name,
            )
        else:
            await message.reply(caption=message.text, file=video_file.name)
