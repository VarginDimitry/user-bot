import re

_FLAGS = re.IGNORECASE | re.DOTALL


def _link_re(host: str, path: str = r"[^\s?#]+") -> re.Pattern[str]:
    return re.compile(
        rf"^\s*(https?://)?(?:{host})/{path}/?(?:[?#][^\s]*)?\s*\Z",
        _FLAGS,
    )


class InstaService:
    BASE_URL = "instagram.com"
    REGEXES: tuple[tuple[re.Pattern[str], str | None], ...] = (
        # Instagram: photo, video, carousel, stories, highlights
        (_link_re(r"(?:www\.|m\.)?instagram\.com"), None),
        (_link_re(r"(?:www\.)?instagr\.am"), "instagr.am"),
        (_link_re(r"(?:www\.)?ddinstagram\.com"), "ddinstagram.com"),
        (_link_re(r"(?:www\.)?kkinstagram\.com"), "kkinstagram.com"),
        # Pinterest: photo, video
        (
            _link_re(
                r"(?:www\.|[a-z]{2}\.)?pinterest\.(?:com(?:\.[a-z]{2})?|co\.uk|[a-z]{2})",
                r"pin/[^\s?#]+",
            ),
            None,
        ),
        (_link_re(r"(?:www\.)?pin\.it"), None),
        # TikTok: video, photo, carousel
        (
            _link_re(r"(?:www\.|m\.)?tiktok\.com", r"@[^\s/]+/(?:video|photo)/\d+"),
            None,
        ),
        (_link_re(r"(?:www\.)?tiktok\.com", r"t/[A-Za-z0-9]+"), None),
        (_link_re(r"(?:www\.)?(?:vm|vt)\.tiktok\.com", r"[A-Za-z0-9]+"), None),
        (_link_re(r"m\.tiktok\.com", r"v/\d+(?:\.html)?"), None),
        # Threads: text, photo, video, carousel, author's threads
        (
            _link_re(r"(?:www\.)?threads\.(?:net|com)", r"@[^\s/]+/post/[A-Za-z0-9_-]+"),
            None,
        ),
        (_link_re(r"(?:www\.)?threads\.(?:net|com)", r"t/[A-Za-z0-9_-]+"), None),
        (_link_re(r"(?:www\.)?threads\.(?:net|com)", r"@[^\s/]+"), None),
    )

    @classmethod
    def process_url(cls, url: str) -> str:
        url = url.strip()

        for regex, source_host in cls.REGEXES:
            if regex.match(url) and source_host:
                url = url.replace(source_host, cls.BASE_URL)

        if (idx := url.find("?")) != -1:
            url = url[:idx]

        return url

    @classmethod
    def check_link_match(cls, url: str | None) -> bool:
        if not url:
            return False
        url = url.strip()
        return any(regex.match(url) for regex, _ in cls.REGEXES)
