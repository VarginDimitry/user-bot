import asyncio
from functools import wraps
import json
from typing import Any, Awaitable
import aiofiles
import re
from logging import Logger
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, ChallengeUnknownStep, ClientUnauthorizedError

from config import Config
from dto.instagram import MyMedia


class BaseInstaService:
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

    async def login(self, force: bool = False) -> bool:
        if force:
            self._clear_session()
        elif self.LOGIN_JSON_PATH.exists() and self.LOGIN_JSON_PATH.is_file():
            async with aiofiles.open(self.LOGIN_JSON_PATH, "r") as f:
                self.client.set_settings(json.loads(await f.read()))

        is_login = await asyncio.to_thread(self._login)

        if is_login:
            async with aiofiles.open(self.LOGIN_JSON_PATH, "w") as f:
                await f.write(json.dumps(self.client.get_settings()))

        return is_login

    def _clear_session(self) -> None:
        if self.LOGIN_JSON_PATH.exists():
            self.LOGIN_JSON_PATH.unlink()
        self.client.set_settings({})

    @classmethod
    def shield_unauthorized(cls, func: Awaitable[Any]) -> Awaitable[Any]:
        @wraps(func)
        async def inner(*args, **kwargs) -> Any:
            self: BaseInstaService = args[0]
            try:
                return await func(*args, **kwargs)
            except (ChallengeUnknownStep, ChallengeRequired, ClientUnauthorizedError) as e:
                self.logger.warning(f"Auth challenge encountered, retrying with fresh login: {e}")
                is_login = await self.login(force=True)
                if is_login:
                    return await func(*args, **kwargs)
                raise
        return inner

    def _login(self) -> bool:
        return self.client.login(
            username=self.config.instagram.username,
            password=self.config.instagram.password,
        )

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


class InstaService(BaseInstaService):
    @BaseInstaService.shield_unauthorized
    async def get_media_info_by_link(self, url: str) -> MyMedia:
        try:
            media_info = await asyncio.to_thread(
                self.client.media_info, self.client.media_pk_from_url(url)
            )
            return MyMedia.model_validate(media_info, from_attributes=True)
        except Exception as e:
            self.logger.error(e)
            raise