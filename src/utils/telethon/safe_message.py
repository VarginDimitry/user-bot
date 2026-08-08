import typing
from typing import Any, Final, Iterable, TYPE_CHECKING

from telethon import hints, TelegramClient
from telethon.tl import types

from utils.strings import split_by_size


class SafeMessageMixin:  # type: ignore[misc]
    MESSAGE_SIZE_LIMIT: Final[int] = 4096
    CAPTION_SIZE_LIMIT: Final[int] = 1024
    CAPTION_SIZE_LIMIT_WITH_PREMIUM: Final[int] = 2048

    if TYPE_CHECKING:

        async def send_message(
            self: "TelegramClient",
            entity: "hints.EntityLike",
            message: "hints.MessageLike" = "",
            *,
            reply_to: "typing.Union[int, types.Message]" = None,
            attributes: "typing.Sequence[types.TypeDocumentAttribute]" = None,
            parse_mode: typing.Optional[str] = (),
            formatting_entities: typing.Optional[
                typing.List[types.TypeMessageEntity]
            ] = None,
            link_preview: bool = True,
            file: "typing.Union[hints.FileLike, typing.Sequence[hints.FileLike]]" = None,
            thumb: "hints.FileLike" = None,
            force_document: bool = False,
            clear_draft: bool = False,
            buttons: typing.Optional["hints.MarkupLike"] = None,
            silent: bool = None,
            background: bool = None,
            supports_streaming: bool = False,
            schedule: "hints.DateLike" = None,
            comment_to: "typing.Union[int, types.Message]" = None,
            nosound_video: bool = None,
            send_as: typing.Optional["hints.EntityLike"] = None,
            message_effect_id: typing.Optional[int] = None,
        ) -> "types.Message":
            pass

    async def safe_send_message(
        self,
        entity: hints.EntityLike,
        message: str = "",
        style: str | None = None,
        **kwargs: Any,
    ) -> list[types.Message]:
        messages: Iterable[str] = split_by_size(message, self.MESSAGE_SIZE_LIMIT)
        if style:
            messages = (f"<{style}>{m}</{style}>" for m in messages)

        return [
            await self.send_message(
                entity,
                m,
                **kwargs,
            )
            for m in messages
        ]
