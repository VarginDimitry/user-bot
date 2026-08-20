from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import BaseSQLModel


class GPTMessageModel(BaseSQLModel):
    __tablename__ = "gpt_message"

    message: Mapped[str] = mapped_column(Text)
    role: Mapped[str]
    role_id: Mapped[str]  # telegram_id for user, model name for gpt
    source_message_id: Mapped[str]
    dialog_id: Mapped[str]
