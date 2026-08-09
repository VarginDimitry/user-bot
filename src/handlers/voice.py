from logging import Logger
from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import Channel, Chat, User

from config import CAPTION_SIZE_LIMIT, CAPTION_SIZE_LIMIT_WITH_PREMIUM, Config
from services.voice_service import VoiceService
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

voice_router = UpdateRouter()


async def auto_transcribe_voice_func_filter(event: NewMessage.Event) -> bool:
    message = cast(Message, event.message)
    chat = cast(User | Chat | Channel, await message.get_chat())

    client = cast(TelegramClient, event.client)
    config = await client.di_container.get(Config)

    if not (message.voice or message.video_note):
        return False

    if chat.id in config.whisper.black_list:
        return False

    if chat.id in config.whisper.white_list:
        return True

    return event.is_private


@voice_router.on(NewMessage(func=auto_transcribe_voice_func_filter))
async def auto_transcribe_voice(
    message: Message,
    client: FromDishka[TelegramClient],
    voice_service: FromDishka[VoiceService],
) -> None:
    result = await voice_service.transcribe_voice_message(message) or "No text detected"

    common_args = {
        "style": "blockquote",
        "parse_mode": "HTML",
        "entity": message.peer_id,
    }

    sender = cast(User, await message.get_sender())
    if sender.is_self and len(result) < (
        CAPTION_SIZE_LIMIT_WITH_PREMIUM if sender.premium else CAPTION_SIZE_LIMIT
    ):
        return await client.edit_message(
            message=message.id,
            text=result,
            **common_args,
        )

    return await client.safe_send_message(
        silent=True,
        message=result,
        reply_to=message.id,
        **common_args,
    )


@voice_router.on(
    NewMessage(func=lambda e: e.message.is_reply, pattern=r"(?i)^в\s+текст\b")
)
async def transcribe_voice(
    message: Message,
    client: FromDishka[TelegramClient],
    logger: FromDishka[Logger],
    voice_service: FromDishka[VoiceService],
) -> None:
    reply_message = cast(Message | None, await message.get_reply_message())
    if not (reply_message and (reply_message.voice or reply_message.video_note)):
        logger.error("Got not a voice message")
        return

    result = (
        await voice_service.transcribe_voice_message(reply_message)
        or "No text detected"
    )

    await message.delete()
    await client.safe_send_message(
        entity=message.peer_id,
        message=result,
        style="blockquote",
        reply_to=message.reply_to_msg_id,
        silent=True,
        parse_mode="HTML",
    )
