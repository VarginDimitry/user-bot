from models import VoiceCacheModel
from repositories.base import BaseRepository


class VoiceCacheRepository(BaseRepository[VoiceCacheModel]):
    model_type = VoiceCacheModel
    id_attribute = "message_id"
