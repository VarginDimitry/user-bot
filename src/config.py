from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class UserBotSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    app_name: str = "Telethon"
    api_id: int
    api_hash: str


class LoggerSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    bot_token: str
    error_logger_send_to: int


class WhisperSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    model: str = "large-v3"
    device: str = "cpu"
    compute_type: str = "int8"
    cpu_threads: int = 1
    download_root: str = "downloads/whisper"

    black_list: list[int] = Field(default_factory=list)


class GeminiSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    api_key: str


class InstaSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    delay_from: int = 2  # in sec
    delay_to: int = 4  # in sec
    username: str
    password: str
    black_list: list[int] = Field(default_factory=list)


class RootConfig(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    user_bot: UserBotSettings
    logger: LoggerSettings

    instagram: InstaSettings
    gemini: GeminiSettings
    whisper: WhisperSettings
