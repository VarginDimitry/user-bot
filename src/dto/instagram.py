from enum import IntEnum

from instagrapi.types import Media
from pydantic import BaseModel, HttpUrl


class MediaType(IntEnum):
    IMAGE = 1
    VIDEO = 2
    ALBUM = 8


class Candidate(BaseModel):
    url: HttpUrl
    height: int
    width: int


class Images(BaseModel):
    candidates: list[Candidate]

    @property
    def bigger(self) -> Candidate | None:
        if not self.candidates:
            return None
        return self.candidates[0]


class MyMedia(Media):
    media_type: MediaType
    image_versions2: Images

    @property
    def bigger_image(self) -> Candidate | None:
        if not self.image_versions2:
            return None
        return self.image_versions2.bigger

    def extract_media_urls(self) -> list[str]:
        match self.media_type:
            case MediaType.IMAGE:
                return [str(self.bigger_image.url)]
            case MediaType.VIDEO:
                return [str(self.video_url)]
            case MediaType.ALBUM:
                return [
                    str(resource.video_url or resource.thumbnail_url)
                    for resource in self.resources
                ]
        return []