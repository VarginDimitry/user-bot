import asyncio
from logging import Logger
from typing import cast

import aiofiles
import ffmpeg
from faster_whisper import WhisperModel
from telethon.tl.patched import Message


class VoiceService:
    def __init__(self, logger: Logger, whisper_model: WhisperModel):
        self.logger = logger
        self.model = whisper_model

    async def transcribe_voice_message(self, message: Message) -> str:
        suffix = ".ogg"
        if message.video_note:
            suffix = ".mp4"

        async with (
            aiofiles.tempfile.NamedTemporaryFile(suffix=suffix) as input_voice,
            aiofiles.tempfile.NamedTemporaryFile(suffix=".wav") as output_voice,
        ):
            path = await message.download_media(file=input_voice.name)
            if not path:
                return ""

            await self.convert_ogg_to_wav(
                cast(str, input_voice.name),
                cast(str, output_voice.name),
            )
            return self.get_transcribe(cast(str, output_voice.name))

    def get_transcribe(self, voice: str) -> str:
        """raise Exception"""
        segments, _ = self.model.transcribe(
            audio=voice, vad_filter=True, beam_size=1, language="ru"
        )
        return "".join([segment.text.strip() for segment in segments]).strip()

    @classmethod
    async def convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        """raise Exception"""
        return await asyncio.to_thread(
            cls.__convert_ogg_to_wav,
            ogg_file_path,
            wav_file_path,
        )

    @classmethod
    def __convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        (
            ffmpeg.input(ogg_file_path)
            .output(wav_file_path, loglevel="quiet")
            .run(overwrite_output=True)
        )
