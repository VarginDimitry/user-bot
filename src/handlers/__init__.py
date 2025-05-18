from telethon.events import NewMessage

from config import BotSettings
from handlers.gpt import ask_gpt
from handlers.insta import download_insta
from handlers.voice import auto_transcribe_voice, transcribe_voice
from utils.custom_telegram_client import MegaTelegramClient


def register_handlers(client: MegaTelegramClient, settings: BotSettings) -> None:
    ### VOICE HANDLERS
    client.add_event_handler(
        auto_transcribe_voice,
        NewMessage(
            func=lambda e: e.message.voice or e.message.video_note,
            chats=settings.BLACK_LIST_VOICE,
            blacklist_chats=True,
        ),
    )
    client.add_event_handler(
        transcribe_voice,
        NewMessage(func=lambda e: e.message.is_reply, pattern=r"^/transcribe$"),
    )

    ### GPT HANDLERS
    client.add_event_handler(
        ask_gpt,
        NewMessage(
            pattern=r"^/gpt",
            outgoing=True,
            incoming=False,
        ),
    )

    ### INSTA HANDLERS
    client.add_event_handler(
        download_insta,
        NewMessage(
            pattern=r"https?://(www\.)?instagram\.com/.*",
            chats=settings.BLACK_LIST_INSTA,
            blacklist_chats=True,
        ),
    )
