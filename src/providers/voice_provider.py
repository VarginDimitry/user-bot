import logging

from dishka import Provider, Scope, provide
from faster_whisper import WhisperModel

from config import WhisperSettings
from services.voice_service import VoiceService


class VoiceProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_whisper_settings(self) -> WhisperSettings:
        return WhisperSettings()

    @provide(scope=Scope.APP)
    def provide_whisper_model(self, whisper_config: WhisperSettings) -> WhisperModel:
        logging.info("voice model start downloading")
        model = WhisperModel(
            model_size_or_path=whisper_config.MODEL,
            device=whisper_config.DEVICE,
            compute_type=whisper_config.COMPUTE_TYPE,
            cpu_threads=whisper_config.CPU_THREADS,
            download_root=whisper_config.DOWNLOAD_ROOT,
        )
        logging.info("voice model has downloaded")
        return model

    @provide(scope=Scope.REQUEST)
    def provide_voice_service(self, whisper_model: WhisperModel) -> VoiceService:
        voice_service = VoiceService(whisper_model=whisper_model)
        return voice_service
