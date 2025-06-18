from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    APP_NAME: str = "Telethon"

    API_ID: int
    API_HASH: str

    BLACK_LIST_INSTA: list[int] = Field(default_factory=list)
    BLACK_LIST_VOICE: list[int] = Field(default_factory=list)


class WhisperSettings(BaseSettings):
    MODEL: str = "large-v3"
    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "int8"
    CPU_THREADS: int = 1
    DOWNLOAD_ROOT: str = "downloads/whisper"

    model_config = SettingsConfigDict(env_prefix="WHISPER_")


class GPTSettings(BaseSettings):
    GOOGLE_GEMINI_API_KEY: str

    model_config = SettingsConfigDict(env_prefix="GPT_")


class InstaSettings(BaseSettings):
    USERNAME: str
    PASSWORD: str

    model_config = SettingsConfigDict(env_prefix="INSTA_")
