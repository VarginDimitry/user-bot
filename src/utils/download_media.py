import asyncio
import os
from uuid import uuid4

import aiofiles
from httpx import AsyncClient

from dto.instagram import MyMedia


async def download_media(
    httpx_client: AsyncClient, tempdir: str, url: str, ext: str
) -> str:
    path = os.path.join(tempdir, f"{uuid4().hex}.{ext}")
    response = await httpx_client.get(url)
    async with aiofiles.open(path, "wb") as f:
        async for chunk in response.aiter_bytes():
            await f.write(chunk)
        return path


async def download_media_by_info(
    httpx_client: AsyncClient, tempdir: str, media_info: MyMedia
) -> str | list[str]:
    if not media_info.is_album():
        return await download_media(
            httpx_client=httpx_client,
            tempdir=tempdir,
            url=str(media_info.video_url or media_info.thumbnail_url),
            ext="mp4" if media_info.is_video() else "jpg",
        )

    download_coroutines = [
        download_media(
            httpx_client=httpx_client,
            tempdir=tempdir,
            url=str(resource.video_url or resource.thumbnail_url),
            ext="mp4" if resource.is_video() else "jpg",
        )
        for resource in media_info.resources
    ]
    return await asyncio.gather(*download_coroutines)
