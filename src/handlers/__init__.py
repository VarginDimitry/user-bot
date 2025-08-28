from typing import cast

from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import User

from config import RootConfig
from handlers.gpt import ask_gpt
from handlers.help import bot_help
from handlers.insta import download_insta
from handlers.voice import auto_transcribe_voice, transcribe_voice
from services.insta_service import InstaService
from utils.custom_telegram_client import MegaTelegramClient


def register_handlers(client: MegaTelegramClient, config: RootConfig) -> None:
    ### HELP HANDLERS
    client.add_event_handler(
        bot_help,
        NewMessage(
            pattern=r"^/help$",
            outgoing=True,
            incoming=False,
        ),
    )

    ### VOICE HANDLERS
    client.add_event_handler(
        auto_transcribe_voice,
        NewMessage(
            func=lambda e: (e.message.voice or e.message.video_note) and e.is_private,
            chats=config.whisper.black_list,
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
    async def download_insta_func_filter(event: NewMessage.Event) -> bool:
        message = cast(Message, event.message)
        user = cast(User, await message.get_sender())

        if user.id in config.instagram.black_list:
            return False

        return bool(user.is_self) or bool(event.is_private)

    client.add_event_handler(
        download_insta,
        NewMessage(
            pattern=InstaService.LINK_REGEX,
            func=download_insta_func_filter,
        ),
    )
