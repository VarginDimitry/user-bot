from models import VoiceCacheModel
from repositories.base import BaseRepository


class VoiceCacheRepository(BaseRepository[VoiceCacheModel]):
    model_type = VoiceCacheModel
    id_attribute = "message_id"

    async def lock_wait(self, message_id: int) -> None:
        return await self._lock_wait(f"voice_cache_{message_id}")

    async def lock_nowait(self, message_id: int) -> bool:
        return await self._lock_nowait(f"voice_cache_{message_id}")
