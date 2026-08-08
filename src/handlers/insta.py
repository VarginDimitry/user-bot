import time
from logging import Logger
from typing import cast

from dishka import FromDishka
from telethon.events import NewMessage
from telethon.tl.patched import Message
from telethon.tl.types import Channel, Chat, User

from config import Config
from services.insta_service import InstaService
from utils.telethon import TelegramClient
from utils.telethon.router import UpdateRouter

insta_router = UpdateRouter()


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

    insta_url = InstaService.process_url(message.text)

    async with client.conversation(
        config.instagram.download_bot_id,
        timeout=config.instagram.download_bot_timeout,
    ) as conv:
        await conv.send_message(insta_url)
        media_message: Message = await conv.get_response()
        file = media_message.media

    time_taken = time.perf_counter() - start_time
    logger.info(f"Download time: {time_taken} seconds")

    await client.safe_send_message(
        entity=message.peer_id,
        file=file,
        message=_build_answer_text(insta_url, time_taken),
        reply_to=message.reply_to_msg_id if user.is_self else message.id,
        silent=True,
        parse_mode="HTML",
    )
    if user.is_self:
        await message.delete()
    return None


def _build_answer_text(url: str, time_taken: float) -> str:
    return f"Download time: {time_taken:.2f} seconds\n{url}\n"
