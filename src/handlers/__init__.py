from telethon import TelegramClient
from telethon.events import NewMessage

from handlers.voice import auto_transcribe_voice, transcribe_voice


def register_handlers(client: TelegramClient):
    ### VOICE HANDLERS
    client.add_event_handler(
        auto_transcribe_voice,
        NewMessage(
            func=lambda e: (e.message.voice or e.message.video_note) and e.is_private
        )
    )
    client.add_event_handler(
        transcribe_voice,
        NewMessage(
            func=lambda e: e.message.is_reply,
            pattern=r'^/transcribe$'
        )
    )
