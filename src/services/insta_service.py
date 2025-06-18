import asyncio
from logging import Logger
from pathlib import Path
from typing import cast

from aiofiles.threadpool.binary import AsyncBufferedReader
from instagrapi import Client
from instagrapi.types import Media

from config import InstaSettings


class InstaService:
    LOGIN_JSON_PATH = Path("InstagramSession.json")

    def __init__(
        self, logger: Logger, config: InstaSettings, insta_client: Client
    ) -> None:
        self.logger = logger
        self.config = config
        self.client = insta_client

    async def login(self) -> None:
        return await asyncio.to_thread(self._login)

    async def download(self, url: str, video_file: AsyncBufferedReader) -> None:
        video_path = Path(cast(str, video_file.name))

        try:
            media_pk = await asyncio.to_thread(self.client.media_pk_from_url, url)
            media_info = await asyncio.to_thread(self.client.media_info, media_pk)
            await asyncio.to_thread(
                self.client.video_download_by_url,
                url=cast(str, media_info.video_url),
                filename=video_path.name,
                folder=video_path.parent,
            )
        except Exception as e:
            # logging.error(f"Failed to download video: {e}")
            raise e

    async def get_media_info_by_link(self, url: str) -> Media:
        try:
            media_pk = await asyncio.to_thread(self.client.media_pk_from_url, url)
            return await asyncio.to_thread(self.client.media_info, media_pk)
        except Exception as e:
            # logging.error(f"Failed to download video: {e}")
            raise e

    def _login(self) -> None:
        if self.LOGIN_JSON_PATH.exists() and self.LOGIN_JSON_PATH.is_file():
            self.client.load_settings(self.LOGIN_JSON_PATH)
        self.client.login(
            username=self.config.USERNAME,
            password=self.config.PASSWORD,
        )
        self.client.dump_settings(self.LOGIN_JSON_PATH)
