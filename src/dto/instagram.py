from enum import IntEnum

from instagrapi.types import Media, Resource
from pydantic import BaseModel, Field, HttpUrl


class MediaType(IntEnum):
    IMAGE = 1
    VIDEO = 2
    ALBUM = 8


class Candidate(BaseModel):
    url: HttpUrl
    height: int
    width: int


class MyResource(Resource):  # type: ignore[misc]
    pk: str
    video_url: HttpUrl | None = None
    thumbnail_url: HttpUrl
    media_type: MediaType

    def is_image(self) -> bool:
        return self.media_type == MediaType.IMAGE

    def is_video(self) -> bool:
        return self.media_type == MediaType.VIDEO

    def is_album(self) -> bool:
        return self.media_type == MediaType.ALBUM


class Images(BaseModel):
    candidates: list[Candidate]


class MyMedia(Media):  # type: ignore[misc]
    media_type: MediaType
    image_versions2: Images
    resources: list[MyResource] = Field(default_factory=list)

    def is_image(self) -> bool:
        return self.media_type == MediaType.IMAGE

    def is_video(self) -> bool:
        return self.media_type == MediaType.VIDEO

    def is_album(self) -> bool:
        return self.media_type == MediaType.ALBUM

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
