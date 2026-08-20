from logging import Logger

from dishka import provide, Provider, Scope
from google.genai import Client
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from repositories.gpt_message import GPTMessageRepository
from services.gpt_service import GPTService, OpenAIService


class GPTProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_gemini(self, config: Config) -> Client:
        return Client(api_key=config.gemini.api_key)

    @provide(scope=Scope.APP)
    def provide_openai(self, config: Config) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=config.openai.base_url,
            api_key=config.openai.api_key,
        )

    @provide(scope=Scope.REQUEST)
    def provide_gpt_message_repository(
        self, session: AsyncSession
    ) -> GPTMessageRepository:
        return GPTMessageRepository(session=session)

    # @provide(scope=Scope.REQUEST)
    # def provide_gpt_service(self, logger: Logger, gemini: Client) -> GPTService:
    #     return GeminiService(logger=logger, gpt=gemini)

    @provide(scope=Scope.REQUEST)
    def provide_gpt_service(
        self,
        logger: Logger,
        openai: AsyncOpenAI,
        config: Config,
        gpt_message_repository: GPTMessageRepository,
    ) -> GPTService:
        return OpenAIService(
            logger=logger,
            gpt=openai,
            config=config,
            gpt_message_repository=gpt_message_repository,
        )
