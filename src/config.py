from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    API_ID: str
    API_HASH: str
    PHONE: str
    LOGIN: str

class WhisperSettings(BaseSettings):
    MODEL: str = "large-v3"
    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "int8"
    CPU_THREADS: int = 1
    DOWNLOAD_ROOT: str = "downloads/whisper"

    model_config = SettingsConfigDict(env_prefix="WHISPER_")
