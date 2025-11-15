import asyncio
from logging import Logger

from dishka import provide, Provider, Scope
from faster_whisper import WhisperModel
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from repositories.voice_cache import VoiceCacheRepository
from services.gpt_service import GPTService
from services.voice_service import VoiceService


class VoiceProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_whisper_model(
        self, logger: Logger, config: Config
    ) -> WhisperModel:
        logger.info("Voice model start downloading")

        model: WhisperModel = await asyncio.to_thread(
            WhisperModel,
            model_size_or_path=config.whisper.model,
            device=config.whisper.device,
            compute_type=config.whisper.compute_type,
            cpu_threads=config.whisper.cpu_threads,
            download_root=config.whisper.download_root,
        )
        model.logger = logger.getChild("faster_whisper")

        logger.info("Voice model has downloaded")

        return model

    @provide(scope=Scope.REQUEST)
    def provide_voice_cache_repository(
        self, session: AsyncSession
    ) -> VoiceCacheRepository:
        return VoiceCacheRepository(session=session)

    @provide(scope=Scope.REQUEST)
    def provide_voice_service(
        self,
        logger: Logger,
        whisper_model: WhisperModel,
        voice_cache_repository: VoiceCacheRepository,
        gpt_service: GPTService,
    ) -> VoiceService:
        return VoiceService(
            logger=logger,
            whisper_model=whisper_model,
            voice_cache_repository=voice_cache_repository,
            gpt_service=gpt_service,
        )
