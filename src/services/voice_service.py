import asyncio
from logging import Logger
from typing import cast

import ffmpeg
from aiofiles.tempfile import NamedTemporaryFile
from aiofiles.threadpool.binary import AsyncBufferedIOBase
from faster_whisper import WhisperModel
from telethon.tl.patched import Message

from models import VoiceCacheModel
from repositories.voice_cache import VoiceCacheRepository
from services.gpt_service import GPTService


class VoiceService:
    def __init__(
        self,
        logger: Logger,
        whisper_model: WhisperModel,
        voice_cache_repository: VoiceCacheRepository,
        gpt_service: GPTService,
    ):
        self.logger = logger
        self.model = whisper_model
        self.voice_cache_repository = voice_cache_repository
        self.gpt_service = gpt_service

    async def transcribe_voice_message(self, message: Message) -> str:
        voice_id = self.get_voice_id(message)
        if not voice_id:
            return ""
        await self.voice_cache_repository.lock_wait(voice_id)

        if voice_cache := await self.voice_cache_repository.get_one_or_none(
            message_id=voice_id
        ):
            return voice_cache.value

        result = await self._transcribe_voice_message(message)

        await self.voice_cache_repository.add(
            VoiceCacheModel(message_id=voice_id, value=result)
        )
        return result

    async def _transcribe_voice_message(self, message: Message) -> str:
        input_ext = ".mp4" if message.video_note else ".ogg"
        async with NamedTemporaryFile(suffix=input_ext) as input_voice:
            path = await message.download_media(file=input_voice.name)
            if not path:
                self.logger.error("Failed to download voice message")
                return ""

            if result := await self._transcribe_using_gpt(input_voice, input_ext):
                return result

            async with NamedTemporaryFile(suffix=".wav") as output_voice:
                return await self._transcribe_using_local_model(
                    input_voice, output_voice
                )

    async def _transcribe_using_gpt(
        self, input_voice: AsyncBufferedIOBase, input_ext: str
    ) -> str:
        return await self.gpt_service.ask_with_file(
            prompt="Detect the language (usually RU) and generate a transcript of the speech. Send only text, without any additional comments.",
            file_path=input_voice.name,
            mime_type=self.gpt_service.MIME_TYPE_MAP.get(input_ext),
        )

    async def _transcribe_using_local_model(
        self,
        input_voice: AsyncBufferedIOBase,
        output_voice: AsyncBufferedIOBase,
    ) -> str:
        await self._convert_ogg_to_wav(
            str(input_voice.name),
            str(output_voice.name),
        )
        return self._get_transcribe_from_wav(cast(str, output_voice.name))

    def _get_transcribe_from_wav(self, voice: str) -> str:
        try:
            segments, _ = self.model.transcribe(
                audio=voice, vad_filter=True, beam_size=1, language="ru"
            )
        except (ValueError, RuntimeError) as err:
            self.logger.error(err)
            raise
        else:
            return "\n".join([segment.text.strip() for segment in segments]).strip()

    @classmethod
    async def _convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        """raise Exception"""
        return await asyncio.to_thread(
            cls._sync_convert_ogg_to_wav,
            ogg_file_path,
            wav_file_path,
        )

    @classmethod
    def _sync_convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        (
            ffmpeg.input(ogg_file_path)
            .output(wav_file_path, loglevel="quiet")
            .run(overwrite_output=True)
        )

    @classmethod
    def get_voice_id(cls, message: Message) -> int | None:
        if (
            message.media
            and (message.media.voice or message.media.round)
            and message.media.document
        ):
            return message.media.document.id
        return None
