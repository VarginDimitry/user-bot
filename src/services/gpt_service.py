import logging
from abc import ABC, abstractmethod

from google import genai


class GPTService(ABC):
    @abstractmethod
    async def ask(self, prompt: str) -> str | None:
        pass


class GeminiService(GPTService):
    GEMINI_MODELS = [
        "gemini-2.5-pro-exp-03-25",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash-8b",
    ]

    def __init__(self, logger: logging.Logger, gpt: genai.Client) -> None:
        self.logger = logger
        self.gpt = gpt

    async def ask(self, prompt: str) -> str | None:
        for model_name in self.GEMINI_MODELS:
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
