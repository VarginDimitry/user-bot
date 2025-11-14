import json

import pydantic_core
from pydantic import AnyUrl


def json_serializer(*args, **kwargs) -> str:
    return json.dumps(*args, default=pydantic_core.to_jsonable_python, **kwargs)


def remove_async_driver(url: str | AnyUrl) -> str:
    if isinstance(url, AnyUrl):
        url = str(url)
    return url.replace("+asyncpg", "").replace("+aiosqlite", "")
