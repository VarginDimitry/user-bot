import logging
from abc import ABC, abstractmethod
from pathlib import Path

from google import genai
from google.genai.types import File


class GPTService(ABC):
    @abstractmethod
    async def ask(self, prompt: str) -> str | None:
        pass

    @abstractmethod
    async def ask_with_file(
        self, prompt: str, file_path: str | Path, mime_type: str
    ) -> str | None:
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
    MIME_TYPE_MAP = {
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".flac": "audio/flac",
    }

    def __init__(self, logger: logging.Logger, gpt: genai.Client) -> None:
        self.logger = logger
        self.gpt = gpt

    async def ask(self, prompt: str) -> str | None:
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
