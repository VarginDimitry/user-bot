import re
from logging import Logger

from config import RootConfig


class InstaService:
    LINK_REGEX = re.compile(r"https?://(www\.)?instagram\.com/.*")
    DD_LINK_REGEX = re.compile(r"https?://(www\.)?ddinstagram\.com/.*")

    def __init__(self, logger: Logger, config: RootConfig) -> None:
        self.logger = logger
        self.config = config

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
