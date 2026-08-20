from models import GPTMessageModel
from repositories.base import BaseRepository


class GPTMessageRepository(BaseRepository[GPTMessageModel]):
    model_type = GPTMessageModel
