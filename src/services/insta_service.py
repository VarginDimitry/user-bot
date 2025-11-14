import asyncio
import re
from logging import Logger
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

from instagrapi import Client

from config import Config
from dto.instagram import MyMedia

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])


# duplicate of instagrapi functional
# def delay_task(func: F) -> F:
#     @wraps(func)
#     async def _inner(*args: Any, **kwargs: Any) -> Any:
#         self: 'InstaService' = args[0]
#         self.logger.info(f"Delay {func.__name__} delaying in {self.config.instagram.request_delay} sec")
#         await asyncio.sleep(self.config.instagram.request_delay)
#         return await func(*args, **kwargs)
#     return _inner


class InstaService:
    LINK_REGEX = re.compile(r"https?://(www\.)?instagram\.com/.*")
    DD_LINK_REGEX = re.compile(r"https?://(www\.)?ddinstagram\.com/.*")
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

    async def get_new_link(self, link: str) -> str:
        link = self.process_url(link)

        if not self.LINK_REGEX.match(link):
            raise ValueError("Invalid link")

        if self.DD_LINK_REGEX.match(link):
            return link

        return link.replace("instagram.com", "ddinstagram.com")

    @classmethod
    def process_url(cls, url: str) -> str:
        url = url.strip()
        return url[:idx] if (idx := url.find("?")) != -1 else url
