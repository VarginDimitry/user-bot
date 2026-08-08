import re


class InstaService:
    BASE_URL = "instagram.com"
    REGEXES: tuple[tuple[re.Pattern[str], str], ...] = (
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?instagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "instagram.com",
        ),
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?ddinstagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "ddinstagram.com",
        ),
        (
            re.compile(
                r"^\s*(https?://)?(www\.)?kkinstagram\.com/[^\s]+\s*\Z", re.DOTALL
            ),
            "kkinstagram.com",
        ),
    )

    @classmethod
    def process_url(cls, url: str) -> str:
        url = url.strip()

        for regex, base_url in cls.REGEXES:
            if regex.match(url):
                url = url.replace(base_url, cls.BASE_URL)

        if (idx := url.find("?")) != -1:
            url = url[:idx]

        return url

    @classmethod
    def check_link_match(cls, url: str) -> bool:
        url = url.strip()
        return any(regex.match(url) for regex, _ in cls.REGEXES)
