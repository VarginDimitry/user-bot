import base64
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Awaitable, Callable

from google import genai
from google.genai.types import File
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import BaseModel, ConfigDict
from telethon.tl.patched import Message
from uuid_utils import uuid7

from config import Config
from models import GPTMessageModel
from repositories.gpt_message import GPTMessageRepository


class GPTAskResult(BaseModel):
    message: str | None = None
    callback: Callable[[str], Awaitable[None]] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class GPTImage(BaseModel):
    data: bytes
    mime_type: str


class GPTService(ABC):
    SYSTEM_PROMPT = "You are a helpful assistant. Answer short and concise in Russian."
    MIME_TYPE_MAP = {
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".flac": "audio/flac",
    }
    MAX_CHAIN_DEPTH = 20
    MAX_IMAGES = 4
    DEFAULT_IMAGE_PROMPT = "Что изображено на этой картинке?"
    EMPTY_ASK_MESSAGE = "Нечего спрашивать: нет текста и нет картинки."
    config: Config
    logger: logging.Logger
    gpt_message_repository: GPTMessageRepository

    def __init__(
        self, logger: logging.Logger, gpt_message_repository: GPTMessageRepository
    ) -> None:
        self.logger = logger
        self.gpt_message_repository = gpt_message_repository

    async def ask(
        self,
        user_id: str,
        prompt: str,
        message: Message,
    ) -> GPTAskResult:
        self.logger.info(f"User ask GPT: {prompt!r}")

        reply_message = await message.get_reply_message()
        chain = await self._resolve_reply_chain(reply_message)
        history_models = await self._build_history(chain)
        images = await self._collect_images(message, chain)

        prompt = prompt.strip()
        if not prompt:
            if images:
                prompt = self.DEFAULT_IMAGE_PROMPT
            else:
                return GPTAskResult(message=self.EMPTY_ASK_MESSAGE)

        new_message = await self.gpt_message_repository.add(
            GPTMessageModel(
                dialog_id=history_models[-1].dialog_id
                if history_models
                else str(uuid7()),
                message=prompt,
                role="user",
                role_id=user_id,
                source_message_id=str(message.id),
            )
        )
        history_models.append(new_message)

        result = await self._ask(history_models, images=images)
        self.logger.info(f"GPT response: {result or 'No response'!r}")

        if not result or not result.content:
            return GPTAskResult(message="No response")

        content = result.content
        role = result.role or "assistant"

        async def callback(source_message_id: str) -> None:
            await self.gpt_message_repository.add(
                GPTMessageModel(
                    dialog_id=history_models[-1].dialog_id,
                    message=content,
                    role=role,
                    role_id=self.config.openai.model,
                    source_message_id=str(source_message_id),
                )
            )

        return GPTAskResult(message=content, callback=callback)

    async def _resolve_reply_chain(
        self, reply_message: Message | None
    ) -> list[Message]:
        chain: list[Message] = []
        seen: set[int] = set()
        current = reply_message
        while current is not None and len(chain) < self.MAX_CHAIN_DEPTH:
            if current.id in seen:
                break
            seen.add(current.id)
            chain.append(current)
            current = await current.get_reply_message()
        return chain

    async def _build_history(self, chain: list[Message]) -> list[GPTMessageModel]:
        if not chain:
            return []

        tracked_index: int | None = None
        tracked: GPTMessageModel | None = None
        for index, ancestor in enumerate(chain):
            found = await self.gpt_message_repository.get_one_or_none(
                GPTMessageModel.source_message_id == str(ancestor.id)
            )
            if found:
                tracked_index = index
                tracked = found
                break

        if tracked is not None:
            history_models = await self.gpt_message_repository.get_many(
                GPTMessageModel.dialog_id == tracked.dialog_id,
                order_by=(GPTMessageModel.created_at, False),
            )
            dialog_id = tracked.dialog_id
            to_synthesize = chain[:tracked_index]
        else:
            history_models = []
            dialog_id = str(uuid7())
            to_synthesize = chain

        for ancestor in reversed(to_synthesize):
            described = await self._describe_message(ancestor)
            if not described:
                continue
            sender = await ancestor.get_sender()
            history_models.append(
                await self.gpt_message_repository.add(
                    GPTMessageModel(
                        dialog_id=dialog_id,
                        message=described,
                        role="user",
                        role_id=str(sender.id) if sender is not None else "unknown",
                        source_message_id=str(ancestor.id),
                    )
                )
            )

        return history_models

    async def _describe_message(self, message: Message) -> str | None:
        sender = await message.get_sender()
        if sender is not None and getattr(sender, "is_self", False):
            label = "Вы"
        elif sender is not None:
            label = (
                getattr(sender, "first_name", None)
                or getattr(sender, "title", None)
                or getattr(sender, "username", None)
                or str(sender.id)
            )
        else:
            label = "Неизвестный"

        text = (message.raw_text or "").strip()
        has_image = self._has_image(message)
        if not text and not has_image:
            return None

        parts = [f"{label}:"]
        if text:
            parts.append(text)
        if has_image:
            parts.append("[изображение]")
        return " ".join(parts)

    @classmethod
    def _has_image(cls, message: Message) -> bool:
        if message.photo:
            return True
        file = message.file
        return bool(file and file.mime_type and file.mime_type.startswith("image/"))

    async def _download_image(self, message: Message) -> GPTImage | None:
        try:
            data = await message.download_media(file=bytes)
        except Exception:
            self.logger.exception(
                "Failed to download image from message %s", message.id
            )
            return None
        if not isinstance(data, (bytes, bytearray)) or not data:
            return None

        mime_type = "image/jpeg"
        if message.file and message.file.mime_type:
            mime_type = message.file.mime_type
        return GPTImage(data=bytes(data), mime_type=mime_type)

    async def _collect_images(
        self, message: Message, chain: list[Message]
    ) -> list[GPTImage]:
        images: list[GPTImage] = []
        for candidate in (message, *chain):
            if len(images) >= self.MAX_IMAGES:
                break
            if not self._has_image(candidate):
                continue
            image = await self._download_image(candidate)
            if image:
                images.append(image)
        return images

    @staticmethod
    def _to_data_url(image: GPTImage) -> str:
        encoded = base64.b64encode(image.data).decode("ascii")
        return f"data:{image.mime_type};base64,{encoded}"

    @abstractmethod
    async def _ask(
        self,
        messages: list[GPTMessageModel],
        images: list[GPTImage] | None = None,
    ) -> ChatCompletionMessage | None:
        pass


class GeminiService(GPTService):
    GEMINI_MODELS_GENERATING: tuple[str, ...] = (
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-preview-09-2025",
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-lite-preview-09-2025",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    )

    def __init__(self, logger: logging.Logger, gpt: genai.Client) -> None:
        self.logger = logger
        self.gpt = gpt

    async def ask(
        self, user_id: int, source_message_id: str, prompt: str, is_first: bool = True
    ) -> str | None:
        for model_name in self.GEMINI_MODELS_GENERATING:
            try:
                response = await self.gpt.aio.models.generate_content(
                    model=model_name, contents=prompt
                )
                return response.text
            except Exception as e:
                logging.error(f"Ошибка при использовании модели {model_name}: {str(e)}")
                continue
        logging.error("Все модели исчерпали квоту")
        return None

    async def ask_with_file(
        self, prompt: str, file_path: str | Path, mime_type: str
    ) -> str | None:
        try:
            gemini_file = await self._upload_file(file_path, mime_type)
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла {file_path}: {str(e)}")
            return None

        for model_name in self.GEMINI_MODELS_GENERATING:
            try:
                response = await self.gpt.aio.models.generate_content(
                    model=model_name, contents=[prompt, gemini_file]
                )
                return response.text
            except Exception as e:
                logging.error(f"Ошибка при использовании модели {model_name}: {str(e)}")
                continue
        logging.error("Все модели исчерпали квоту")
        return None

    async def _upload_file(self, file_path: str | Path, mime_type: str) -> File:
        return await self.gpt.aio.files.upload(
            file=file_path,
            config={"mime_type": self.MIME_TYPE_MAP.get(mime_type)},
        )


class OpenAIService(GPTService):
    def __init__(
        self,
        logger: logging.Logger,
        gpt: AsyncOpenAI,
        config: Config,
        gpt_message_repository: GPTMessageRepository,
    ) -> None:
        self.logger = logger
        self.gpt = gpt
        self.config = config
        self.gpt_message_repository = gpt_message_repository

    async def _ask(
        self,
        messages: list[GPTMessageModel],
        images: list[GPTImage] | None = None,
    ) -> ChatCompletionMessage | None:
        try:
            payload: list[dict[str, Any]] = [
                {
                    "role": "system",
                    "content": self.SYSTEM_PROMPT,
                }
            ]
            last_index = len(messages) - 1
            for index, message in enumerate(messages):
                if index == last_index and images:
                    content: list[dict[str, Any]] = [
                        {"type": "text", "text": message.message}
                    ]
                    content.extend(
                        {
                            "type": "image_url",
                            "image_url": {"url": self._to_data_url(image)},
                        }
                        for image in images
                    )
                    payload.append({"role": message.role, "content": content})
                else:
                    payload.append(
                        {
                            "role": message.role,
                            "content": message.message,
                        }
                    )

            response = await self.gpt.chat.completions.create(
                model=self.config.openai.model,
                messages=payload,
                stream=False,
            )
            result = response.choices[0].message
            if not result.content:
                raise ValueError("GPT response is empty")
        except Exception:
            self.logger.exception(
                "Failed to call model %s at %s",
                self.config.openai.model,
                self.config.openai.base_url,
            )
            return None

        return result
