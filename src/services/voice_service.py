import asyncio
from logging import Logger
from typing import cast

import ffmpeg
from aiofiles.tempfile import NamedTemporaryFile
from faster_whisper import WhisperModel
from telethon.tl.patched import Message


class VoiceService:
    def __init__(self, logger: Logger, whisper_model: WhisperModel):
        self.logger = logger
        self.model = whisper_model

    async def transcribe_voice_message(self, message: Message) -> str:
        async with (
            NamedTemporaryFile(
                suffix=".mp4" if message.video_note else ".ogg"
            ) as input_voice,
            NamedTemporaryFile(suffix=".wav") as output_voice,
        ):
            path = await message.download_media(file=input_voice.name)
            if not path:
                self.logger.error("Failed to download voice message")
                return ""

            await self.convert_ogg_to_wav(
                cast(str, input_voice.name),
                cast(str, output_voice.name),
            )
            return self.get_transcribe(cast(str, output_voice.name))

    def get_transcribe(self, voice: str) -> str:
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
    async def convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        """raise Exception"""
        return await asyncio.to_thread(
            cls.sync_convert_ogg_to_wav,
            ogg_file_path,
            wav_file_path,
        )

    @classmethod
    def sync_convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        (
            ffmpeg.input(ogg_file_path)
            .output(wav_file_path, loglevel="quiet")
            .run(overwrite_output=True)
        )
