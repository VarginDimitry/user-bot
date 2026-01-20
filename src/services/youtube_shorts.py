from logging import Logger
from typing import Any

from pytubefix import AsyncYouTube

from config import Config


dict()

class YoutubeShortsService:
    # https://youtube.com/shorts/t8lHsAAt-vk?si=ssS23pqpKZqZH3St
    BASE_URL = "youtube.com/shorts"

    def __init__(self, logger: Logger, config: Config) -> None:
        self.logger = logger
        self.config = config
        
    async def get_media_info_by_link(self, url: str) -> dict[str, Any]:
        # url = f"[{url}]({url})"
        youtube = AsyncYouTube(url, 'WEB')
        title = await youtube.title()
        # views = await youtube.views()
        # likes = await youtube.likes()
        # author = await youtube.author()
        asyncio.sleep(2)
        
        video = (await youtube.streams()).get_highest_resolution()

        return {
            "title": title,
            # "views": views,
            # "likes": likes,
            # "author": author,
            "video": video.url,
        }
        

async def main():
    import logging
    import json
    url = "https://youtu.be/Bz0zYP5bWf8?si=iYSh10eRt-rZMnXO"
    service = YoutubeShortsService(logger=logging.getLogger(__name__), config=Config())
    media_info = await service.get_media_info_by_link(url)
    print(json.dumps(media_info, indent=4))
    
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
