from typing import cast

from telethon.events import NewMessage
from telethon.tl.patched import Message

from composite_container import client, voice_service


@client.on(
    NewMessage(
        func=lambda e: (e.message.voice or e.message.video_note) and e.is_private
    )
)
async def transcribe_voices(event: NewMessage.Event):
    message = cast(Message, event.message)
    result = await voice_service.transcribe_voice_message(message) or "No text detected"
    await message.reply(
        message=f"<blockquote>{result}</blockquote>",
        parse_mode="HTML",
    )


if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
