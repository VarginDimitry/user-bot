from logging import Logger

from dishka import provide, Provider, Scope
from google.genai import Client

from config import Config
from services.gpt_service import GeminiService, GPTService


class GPTProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_gemini(self, config: Config) -> Client:
        return Client(api_key=config.gemini.api_key)

    @provide(scope=Scope.REQUEST)
    def provide_gpt_service(self, logger: Logger, gemini: Client) -> GPTService:
        return GeminiService(logger=logger, gpt=gemini)
