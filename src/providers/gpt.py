from dishka import Provider, provide, Scope
from google.genai import Client

from config import GPTSettings
from services.gpt_service import GPTService, GeminiService


class GPTProvider(Provider):

    @provide(scope=Scope.APP)
    def provide_bot_settings(self) -> GPTSettings:
        return GPTSettings()  # type: ignore

    @provide(scope=Scope.APP)
    def provide_gemini(self, gpt_config: GPTSettings) -> Client:
        return Client(api_key=gpt_config.GOOGLE_GEMINI_API_KEY)

    @provide(scope=Scope.REQUEST)
    def provide_gpt_service(self, gemini: Client) -> GPTService:
        return GeminiService(gemini)

