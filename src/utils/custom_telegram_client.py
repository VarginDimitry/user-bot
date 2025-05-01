from typing import Final, Sequence

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection
from telethon import TelegramClient, hints
from telethon.client.updates import Callback
from telethon.events.common import EventBuilder
from telethon.tl import types


class MegaTelegramClient(TelegramClient):
    MESSAGE_SIZE_LIMIT: Final[int] = 4096

    def __init__(self, *args, di_container: AsyncContainer, **kwargs):
        self.di_container = di_container
        super().__init__(*args, **kwargs)

    def add_event_handler(self, callback: Callback, event: EventBuilder = None) -> None:
        di_wrapper = wrap_injection(
            func=callback,
            container_getter=lambda args, kwargs: self.di_container,
            is_async=True,
            manage_scope=True,
        )
        return super().add_event_handler(di_wrapper, event)

    async def safe_send_message(
        self,
        entity: hints.EntityLike,
        message: str = "",
        *,
        reply_to: int | types.Message = None,
        attributes: Sequence[types.TypeDocumentAttribute] = None,
        parse_mode: str | None = (),
        formatting_entities: list[types.TypeMessageEntity] | None = None,
        link_preview: bool = True,
        file: hints.FileLike | Sequence[hints.FileLike] = None,
        thumb: hints.FileLike = None,
        force_document: bool = False,
        clear_draft: bool = False,
        buttons: hints.MarkupLike | None = None,
        silent: bool = None,
        background: bool = None,
        supports_streaming: bool = False,
        schedule: hints.DateLike = None,
        comment_to: int | types.Message = None,
        nosound_video: bool = None,
        send_as: hints.EntityLike | None = None,
        message_effect_id: int | None = None,
    ) -> list[types.Message]:
        messages = split_by_size(message, self.MESSAGE_SIZE_LIMIT)
        return [
            await self.send_message(
                entity,
                m,
                reply_to=reply_to,
                attributes=attributes,
                parse_mode=parse_mode,
                formatting_entities=formatting_entities,
                link_preview=link_preview,
                file=file,
                thumb=thumb,
                force_document=force_document,
                clear_draft=clear_draft,
                buttons=buttons,
                silent=silent,
                background=background,
                supports_streaming=supports_streaming,
                schedule=schedule,
                comment_to=comment_to,
                nosound_video=nosound_video,
                send_as=send_as,
                message_effect_id=message_effect_id,
            )
            for m in messages
        ]


def split_by_size(text: str, max_size: int) -> list[str]:
    return [text[i : i + max_size] for i in range(0, len(text), max_size)]
