import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Awaitable, Callable

from google import genai
from google.genai.types import File
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import BaseModel, ConfigDict
from uuid_utils import uuid7

from config import Config
from models import GPTMessageModel
from repositories.gpt_message import GPTMessageRepository


class GPTAskResult(BaseModel):
    message: str | None = None
    callback: Callable[[str], Awaitable[None]] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


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
        prompt_message_id: str,
        reply_message_id: str | None = None,
    ) -> GPTAskResult:
        self.logger.info(f"User ask GPT: {prompt!r}")

        history_models = await self._get_history(reply_message_id)
        new_message = await self.gpt_message_repository.add(
            GPTMessageModel(
                dialog_id=history_models[-1].dialog_id
                if history_models
                else str(uuid7()),
                message=prompt,
                role="user",
                role_id=user_id,
                source_message_id=prompt_message_id,
            )
        )
        history_models.append(new_message)

        result = await self._ask(history_models)
        self.logger.info(f"GPT response: {result or 'No response'!r}")

        callback: Callable[[str], None] | None = None
        if result:

            async def callback(source_message_id: str) -> None:
                await self.gpt_message_repository.add(
                    GPTMessageModel(
                        dialog_id=history_models[-1].dialog_id,
                        message=result.content,
                        role=result.role,
                        role_id=self.config.openai.model,
                        source_message_id=str(source_message_id),
                    )
                )

        return GPTAskResult(message=result.content or "No response", callback=callback)

    async def _get_history(
        self,
        reply_message_id: str | None = None,
    ) -> list[GPTMessageModel]:
        if not reply_message_id:
            return []

        reply_message = await self.gpt_message_repository.get_one(
            GPTMessageModel.source_message_id == reply_message_id
        )
        if not reply_message:
            return []

        history_models = await self.gpt_message_repository.get_many(
            GPTMessageModel.dialog_id == reply_message.dialog_id
        )
        if not history_models:
            return []

        return history_models

    @abstractmethod
    async def _ask(
        self, messages: list[dict[str, str]]
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
        self, messages: list[GPTMessageModel]
    ) -> ChatCompletionMessage | None:
        try:
            response = await self.gpt.chat.completions.create(
                model=self.config.openai.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    *[
                        {
                            "role": message.role,
                            "content": message.message,
                        }
                        for message in messages
                    ],
                ],
                stream=False,
            )
            result = response.choices[0].message
            if not result.content:
                raise ValueError("GPT response is empty")
        except Exception as e:
            logging.error(
                f"Ошибка при использовании модели {self.config.openai.model}: {str(e)}"
            )
            return None

        return result
