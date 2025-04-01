import logging

from dotenv import load_dotenv
from pyrogram import Client

from voice_service import VoiceService
from config import BotSettings

load_dotenv()

config = BotSettings()  # type: ignore

bot = Client(
    name=config.LOGIN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.PHONE,
)

logging.info("voice model start downloading")
voice_service = VoiceService()
logging.info("voice model has downloaded")
