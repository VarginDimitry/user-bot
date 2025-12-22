from pydantic import AnyUrl, ConfigDict, Field
from pydantic_settings import BaseSettings


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


class GeminiSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    api_key: str


class InstaSettings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    delay_from: int = 1  # in sec
    delay_to: int = 2  # in sec
    username: str
    password: str
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
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    user_bot: UserBotSettings
    logger: LoggerSettings

    instagram: InstaSettings
    gemini: GeminiSettings
    whisper: WhisperSettings

    sqlite: SqliteSettings | None = None
    postgres: PostgresConfig | None = None

    # @model_validator(mode="after")
    # def validate_database(self) -> "Config":
    #     if bool(self.sqlite) ^ bool(self.postgres):
    #         return self
    #     raise ValueError("Only one database can be used")
