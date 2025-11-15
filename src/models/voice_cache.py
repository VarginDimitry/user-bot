from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import NoIDSQLModel


class VoiceCacheModel(NoIDSQLModel):
    __tablename__ = "voice_cache"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    value: Mapped[str]
