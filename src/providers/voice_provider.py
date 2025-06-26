import asyncio
from logging import Logger

from dishka import provide, Provider, Scope
from faster_whisper import WhisperModel

from config import WhisperSettings
from services.voice_service import VoiceService


class VoiceProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_whisper_settings(self) -> WhisperSettings:
        return WhisperSettings()

    @provide(scope=Scope.APP)
    async def provide_whisper_model(
        self, logger: Logger, whisper_config: WhisperSettings
    ) -> WhisperModel:
        logger.info("Voice model start downloading")

        model: WhisperModel = await asyncio.to_thread(
            WhisperModel,
            model_size_or_path=whisper_config.MODEL,
            device=whisper_config.DEVICE,
            compute_type=whisper_config.COMPUTE_TYPE,
            cpu_threads=whisper_config.CPU_THREADS,
            download_root=whisper_config.DOWNLOAD_ROOT,
        )
        model.logger = logger.getChild("faster_whisper")

        logger.info("Voice model has downloaded")

        return model

    @provide(scope=Scope.REQUEST)
    def provide_voice_service(
        self, logger: Logger, whisper_model: WhisperModel
    ) -> VoiceService:
        return VoiceService(logger=logger, whisper_model=whisper_model)
