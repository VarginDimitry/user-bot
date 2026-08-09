from pathlib import Path
from typing import Final

from pydantic import AnyUrl, ConfigDict, Field
from pydantic_settings import BaseSettings

MESSAGE_SIZE_LIMIT: Final[int] = 4096
CAPTION_SIZE_LIMIT: Final[int] = 1024
CAPTION_SIZE_LIMIT_WITH_PREMIUM: Final[int] = 2048

# App cwd is often `src/`; keep .env at the repo root.
_ENV_FILE: Final[Path] = Path(__file__).resolve().parent.parent / ".env"


class UserBotSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    app_name: str = "Telethon"
    api_id: int
    api_hash: str


class LoggerSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    enable_telegram: bool = True
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
    white_list: list[int] = Field(default_factory=list)


class GeminiSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    api_key: str


class OpenAISettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    base_url: str
    api_key: str = "cursor"
    model: str = "cursor-grok-4.5-low"


class InstaSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    download_bot_id: int = 523131145
    download_bot_timeout: float = 120

    black_list: list[int] = Field(default_factory=list)


class SqliteSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    path: str
    echo: bool = True


class PostgresConfig(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    dns: AnyUrl
    echo: bool = True
    max_pool_size: int = 5

    @property
    def dns_driver(self) -> str:
        dns = str(self.dns)
        return dns[: dns.index(":")]

    @property
    def dns_dialect(self) -> str:
        driver = self.dns_driver
        if (plus_index := driver.find("+")) != -1:
            driver = driver[:plus_index]
        return driver


class Config(BaseSettings):
    model_config = ConfigDict(
        extra="ignore",
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    user_bot: UserBotSettings
    logger: LoggerSettings

    instagram: InstaSettings
    gemini: GeminiSettings
    openai: OpenAISettings
    whisper: WhisperSettings

    sqlite: SqliteSettings | None = None
    postgres: PostgresConfig | None = None

    # @model_validator(mode="after")
    # def validate_database(self) -> "Config":
    #     if bool(self.sqlite) ^ bool(self.postgres):
    #         return self
    #     raise ValueError("Only one database can be used")
