import asyncio
from pathlib import Path
from typing import cast

from aiofiles.threadpool.binary import AsyncBufferedReader
from instagrapi import Client
from instagrapi.types import Media
from pydantic import AnyUrl


class InstaService:
    def __init__(self, insta_client: Client) -> None:
        self.insta_client = insta_client

    async def download(self, url: str, video_file: AsyncBufferedReader) -> None:
        video_path = Path(video_file.name)

        try:
            media_pk = await asyncio.to_thread(self.insta_client.media_pk_from_url,url)
            media_info = await asyncio.to_thread(self.insta_client.media_info, media_pk)
            await asyncio.to_thread(
                self.insta_client.video_download_by_url,
                url=cast(str, media_info.video_url),
                filename=video_path.name,
                folder=video_path.parent,
            )
        except Exception as e:
            # logging.error(f"Failed to download video: {e}")
            raise e

    async def get_media_info_by_link(self, url: str) -> Media:
        try:
            media_pk = await asyncio.to_thread(self.insta_client.media_pk_from_url,url)
            return await asyncio.to_thread(self.insta_client.media_info, media_pk)
        except Exception as e:
            # logging.error(f"Failed to download video: {e}")
            raise e
