from logging import Logger

from dishka import Provider, Scope, provide
from google.genai import Client

from config import GPTSettings
from services.gpt_service import GeminiService, GPTService


class GPTProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> GPTSettings:
        return GPTSettings()

    @provide(scope=Scope.APP)
    def provide_gemini(self, gpt_config: GPTSettings) -> Client:
        return Client(api_key=gpt_config.GOOGLE_GEMINI_API_KEY)

    @provide(scope=Scope.REQUEST)
    def provide_gpt_service(self, logger: Logger, gemini: Client) -> GPTService:
        return GeminiService(logger=logger, gpt=gemini)
