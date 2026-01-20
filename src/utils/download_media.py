import asyncio
from logging import Logger
import os
from uuid import uuid4

import aiofiles
from httpx import AsyncClient

from dto.instagram import MyMedia

TmpDirType = type("TmpDirType", (str,), {})


class DownloadService:
    def __init__(self, logger: Logger, httpx_client: AsyncClient, tempdir: str):
        self.logger = logger
        self.httpx_client = httpx_client
        self.tempdir = tempdir

    async def download_media(self, url: str, ext: str) -> str:
        self.logger.info(f"Downloading media from {url}")
        path = os.path.join(self.tempdir, f"{uuid4().hex}.{ext}")
        response = await self.httpx_client.get(url)
        async with aiofiles.open(path, "wb") as f:
            async for chunk in response.aiter_bytes():
                await f.write(chunk)
        
        # Compress video if it's an mp4 file
        if ext == "mp4":
            path = await self._compress_video(path)
            
        return path

    async def download_media_by_info(self, media_info: MyMedia) -> str | list[str]:
        if not media_info.is_album():
            return await self.download_media(
                url=str(media_info.video_url or media_info.thumbnail_url),
                ext="mp4" if media_info.is_video() else "jpg",
            )

        download_coroutines = [
            self.download_media(
                url=str(resource.video_url or resource.thumbnail_url),
                ext="mp4" if resource.is_video() else "jpg",
            )
            for resource in media_info.resources
        ]
        return await asyncio.gather(*download_coroutines)

    async def _compress_video(self, input_path: str) -> str:
        self.logger.info(f"Compressing video from {input_path}")
        output_path = os.path.join(self.tempdir, f"{uuid4().hex}.mp4")
        
        # ffmpeg command for compression:
        # - crf 28: quality level (0-51, higher = smaller file, 23 is default, 28 is good compression)
        # - preset fast: encoding speed/compression ratio tradeoff
        # - vcodec libx264: use H.264 codec
        # - acodec aac: use AAC audio codec
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-preset", "fast",
            "-acodec", "aac",
            "-y",  # Overwrite output file if it exists
            output_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        
        await process.wait()
        
        if process.returncode != 0:
            # If compression fails, return original file
            return input_path
        
        # Remove the original file and return compressed version
        try:
            os.remove(input_path)
        except Exception:
            pass
            
        return output_path
