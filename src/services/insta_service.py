import asyncio
import re
from logging import Logger
from pathlib import Path

from instagrapi import Client

from config import Config
from dto.instagram import MyMedia


class InstaService:
    BASE_URL = "instagram.com"
    REGEXES: tuple[tuple[re.Pattern[str], str], ...] = (
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?instagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "instagram.com",
        ),
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?ddinstagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "ddinstagram.com",
        ),
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?kkinstagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "kkinstagram.com",
        ),
    )
    LOGIN_JSON_PATH = Path("InstagramSession.json")

    def __init__(self, logger: Logger, config: Config, insta_client: Client) -> None:
        self.logger = logger
        self.config = config
        self.client = insta_client

    async def login(self) -> bool:
        return await asyncio.to_thread(self._login)

    async def get_media_info_by_link(self, url: str) -> MyMedia:
        try:
            media_info = await asyncio.to_thread(
                self.client.media_info, self.client.media_pk_from_url(url)
            )
            return MyMedia.model_validate(media_info, from_attributes=True)
        except Exception as e:
            self.logger.error(e)
            raise

    def _login(self) -> bool:
        if self.LOGIN_JSON_PATH.exists() and self.LOGIN_JSON_PATH.is_file():
            self.client.load_settings(self.LOGIN_JSON_PATH)
        is_login: bool = self.client.login(
            username=self.config.instagram.username,
            password=self.config.instagram.password,
        )
        if is_login:
            self.client.dump_settings(self.LOGIN_JSON_PATH)
        #     return is_login

        # is_login: bool = self.client.login(
        #     username=self.config.instagram.username,
        #     password=self.config.instagram.password,
        #     relogin=True,
        # )
        # if is_login:
        #     self.client.dump_settings(self.LOGIN_JSON_PATH)

        return is_login

    @classmethod
    def process_url(cls, url: str) -> str:
        url = url.strip()

        for regex, base_url in cls.REGEXES:
            if regex.match(url):
                url = url.replace(base_url, cls.BASE_URL)

        if (idx := url.find("?")) != -1:
            url = url[:idx]

        return url

    @classmethod
    def check_link_match(cls, url: str) -> bool:
        url = url.strip()
        return any(regex.match(url) for regex, _ in cls.REGEXES)
