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
    candidates: list[Candidate] = Field(default_factory=list)


class MyMedia(Media):  # type: ignore[misc]
    media_type: MediaType
    image_versions2: Images | None
    resources: list[MyResource] = Field(default_factory=list)

    def is_image(self) -> bool:
        return self.media_type == MediaType.IMAGE

    def is_video(self) -> bool:
        return self.media_type == MediaType.VIDEO

    def is_album(self) -> bool:
        return self.media_type == MediaType.ALBUM
