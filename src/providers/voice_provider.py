import asyncio
from logging import Logger

from dishka import provide, Provider, Scope
from faster_whisper import WhisperModel

from config import RootConfig
from services.voice_service import VoiceService


class VoiceProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_whisper_model(
        self, logger: Logger, config: RootConfig
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
    def provide_voice_service(
        self, logger: Logger, whisper_model: WhisperModel
    ) -> VoiceService:
        return VoiceService(logger=logger, whisper_model=whisper_model)
