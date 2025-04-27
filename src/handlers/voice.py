from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message

from services.voice_service import VoiceService


async def auto_transcribe_voice(event: NewMessage.Event, voice_service: FromDishka[VoiceService]):
    message = cast(Message, event.message)
    result = await voice_service.transcribe_voice_message(message) or "No text detected"
    await message.reply(
        message=f"<blockquote>{result}</blockquote>",
        parse_mode="HTML",
    )


async def transcribe_voice(event: NewMessage.Event, voice_service: FromDishka[VoiceService]):
    message = cast(Message, event.message)
    reply_message = cast(Message | None, await message.get_reply_message())
    if not (reply_message and (reply_message.voice or reply_message.video_note)):
        return

    result = await voice_service.transcribe_voice_message(reply_message) or "No text detected"
    await message.edit(
        text=f"<blockquote>{result}</blockquote>",
        parse_mode="HTML",
    )