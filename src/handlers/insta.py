import time
from logging import Logger
from typing import Any, cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import Channel, Chat, MessageMediaDocument, MessageMediaPhoto, User

from config import CAPTION_SIZE_LIMIT, Config
from services.insta_service import InstaService
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

insta_router = UpdateRouter()

_FOLLOWUP_TIMEOUT = 8.0
_ALBUM_SIZE = 10


async def download_insta_func_filter(event: NewMessage.Event) -> bool:
    message = cast(Message, event.message)
    sender = cast(User, await message.get_sender())
    chat = cast(User | Chat | Channel, await message.get_chat())

    client = cast(TelegramClient, event.client)
    config = await client.di_container.get(Config)

    if chat.id in config.instagram.black_list:
        return False

    if isinstance(chat, User) and chat.bot:
        return False

    if not InstaService.check_link_match(message.text):
        return False

    return bool(sender.is_self) or bool(event.is_private)


@insta_router.on(NewMessage(func=download_insta_func_filter))
async def download_insta(
    message: Message,
    client: FromDishka[TelegramClient],
    user: FromDishka[User],
    logger: FromDishka[Logger],
    config: FromDishka[Config],
) -> None:
    start_time = time.perf_counter()

    source_url = InstaService.process_url(message.text)

    async with client.conversation(
        config.instagram.download_bot_id,
        timeout=config.instagram.download_bot_timeout,
    ) as conv:
        await conv.send_message(source_url)
        responses = await _collect_bot_responses(conv)

    time_taken = time.perf_counter() - start_time
    logger.info(f"Download time: {time_taken} seconds")

    await _send_download_results(
        client=client,
        peer=message.peer_id,
        responses=responses,
        header=_build_answer_text(source_url, time_taken),
        reply_to=message.reply_to_msg_id if user.is_self else message.id,
    )
    if user.is_self:
        await message.delete()
    return None


def _build_answer_text(url: str, time_taken: float) -> str:
    return f"Download time: {time_taken:.2f} seconds\n{url}\n"


async def _collect_bot_responses(conv: Any) -> list[Message]:
    responses = [await conv.get_response()]
    while True:
        try:
            responses.append(await conv.get_response(timeout=_FOLLOWUP_TIMEOUT))
        except TimeoutError:
            break
    return responses


def _media_payload(message: Message) -> MessageMediaPhoto | MessageMediaDocument | None:
    media = message.media
    if isinstance(media, (MessageMediaPhoto, MessageMediaDocument)):
        return media
    return None


def _chunks[T](items: list[T], size: int) -> list[list[T]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


async def _send_download_results(
    *,
    client: TelegramClient,
    peer: object,
    responses: list[Message],
    header: str,
    reply_to: int | None,
) -> None:
    header_sent = False
    media_batch: list[MessageMediaPhoto | MessageMediaDocument] = []
    media_captions: list[str] = []

    async def flush_media() -> None:
        nonlocal header_sent, media_batch, media_captions
        if not media_batch:
            return

        extra = "\n\n".join(caption for caption in media_captions if caption)
        caption = ""
        parse_mode: str | None = "HTML"
        if not header_sent:
            caption = f"{header}\n{extra}" if extra else header
            if extra:
                parse_mode = None
            if len(caption) > CAPTION_SIZE_LIMIT:
                await client.safe_send_message(
                    entity=peer,
                    message=caption,
                    reply_to=reply_to,
                    silent=True,
                )
                caption = ""
            header_sent = True

        for index, chunk in enumerate(_chunks(media_batch, _ALBUM_SIZE)):
            file = chunk[0] if len(chunk) == 1 else chunk
            chunk_caption = caption if index == 0 else ""
            if chunk_caption:
                await client.safe_send_message(
                    entity=peer,
                    file=file,
                    message=chunk_caption,
                    reply_to=reply_to,
                    silent=True,
                    parse_mode=parse_mode,
                )
            else:
                await client.send_message(
                    peer,
                    file=file,
                    reply_to=reply_to,
                    silent=True,
                )

        media_batch = []
        media_captions = []

    for response in responses:
        file = _media_payload(response)
        if file is not None:
            media_batch.append(file)
            if response.message:
                media_captions.append(response.message)
            continue

        await flush_media()
        text = response.message or ""
        if not header_sent:
            body = f"{header}\n{text}" if text else header
            header_sent = True
        elif text:
            body = text
        else:
            continue
        await client.safe_send_message(
            entity=peer,
            message=body,
            reply_to=reply_to,
            silent=True,
        )

    await flush_media()
    if not header_sent:
        await client.safe_send_message(
            entity=peer,
            message=header,
            reply_to=reply_to,
            silent=True,
            parse_mode="HTML",
        )
