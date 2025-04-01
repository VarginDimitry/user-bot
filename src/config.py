from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    API_ID: str
    API_HASH: str
    PHONE: str
    LOGIN: str
