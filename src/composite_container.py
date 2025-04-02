import logging
import sys

from dotenv import load_dotenv
from pyrogram import Client

from voice_service import VoiceService
from config import BotSettings, WhisperSettings

load_dotenv()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

config = BotSettings()  # type: ignore
whisper_config = WhisperSettings()

bot = Client(
    name=config.LOGIN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.PHONE,
)

logging.info("voice model start downloading")
voice_service = VoiceService(whisper_settings=whisper_config)
logging.info("voice model has downloaded")
