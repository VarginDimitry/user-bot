from logging import Logger
from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from services.voice_service import VoiceService
from utils.custom_telegram_client import MegaTelegramClient


async def auto_transcribe_voice(
    event: NewMessage.Event, voice_service: FromDishka[VoiceService]
) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)
    result = await voice_service.transcribe_voice_message(message) or "No text detected"

    await client.safe_send_message(
        entity=message.peer_id,
        message=result,
        style="blockquote",
        reply_to=message.id,
        silent=True,
        parse_mode="HTML",
    )


async def transcribe_voice(
    event: NewMessage.Event,
    logger: FromDishka[Logger],
    voice_service: FromDishka[VoiceService],
) -> None:
    message = cast(Message, event.message)
    client = cast(MegaTelegramClient, event.client)

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
