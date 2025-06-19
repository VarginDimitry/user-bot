import asyncio
from logging import Logger
from pathlib import Path

from instagrapi import Client

from config import InstaSettings
from dto.instagram import MyMedia


class InstaService:
    LOGIN_JSON_PATH = Path("InstagramSession.json")

    def __init__(
        self, logger: Logger, config: InstaSettings, insta_client: Client
    ) -> None:
        self.logger = logger
        self.config = config
        self.client = insta_client

    async def login(self) -> bool:
        return await asyncio.to_thread(self._login)

    async def get_media_info_by_link(self, url: str) -> MyMedia:
        try:
            media_pk = await asyncio.to_thread(self.client.media_pk_from_url, url)
            return MyMedia.model_validate(
                await asyncio.to_thread(
                    self.client.media_info,
                    media_pk,
                ),
                from_attributes=True,
            )
        except Exception as e:
            # logging.error(f"Failed to download video: {e}")
            raise e

    def _login(self) -> bool:
        if self.LOGIN_JSON_PATH.exists() and self.LOGIN_JSON_PATH.is_file():
            self.client.load_settings(self.LOGIN_JSON_PATH)
        is_login: bool = self.client.login(
            username=self.config.USERNAME,
            password=self.config.PASSWORD,
        )
        if is_login:
            self.client.dump_settings(self.LOGIN_JSON_PATH)
        return is_login

    @classmethod
    def process_url(cls, url: str) -> str:
        url = url.strip()
        if "?" in url:
            url = url[: url.find("?")]
        return url

    @classmethod
    def beautify_int(cls, x: int) -> str:
        char = "-" if x < 0 else ""
        x = abs(x)
        if x < 1_000:
            return f"{char}{x}"
        elif x < 1_000_000:
            return f"{char}{x // 1000}K"
        elif x < 1_000_000_000:
            return f"{char}{x // 1_000_000}M"
        else:
            return f"{char}{x // 1_000_000_000}B"
