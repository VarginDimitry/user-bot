import logging
import sys

from dotenv import load_dotenv
from telethon import TelegramClient

from config import BotSettings, WhisperSettings
from voice_service import VoiceService

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

config = BotSettings()  # type: ignore
whisper_config = WhisperSettings()

client = TelegramClient(
    session="Telethon",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
)

logging.info("voice model start downloading")
voice_service = VoiceService(whisper_settings=whisper_config)
logging.info("voice model has downloaded")
