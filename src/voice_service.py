import logging

import aiofiles
import ffmpeg
from faster_whisper import WhisperModel
from telethon.tl.patched import Message

from config import WhisperSettings


class VoiceService:
    def __init__(self, whisper_settings: WhisperSettings):
        self.model = WhisperModel(
            model_size_or_path=whisper_settings.MODEL,
            device=whisper_settings.DEVICE,
            compute_type=whisper_settings.COMPUTE_TYPE,
            cpu_threads=whisper_settings.CPU_THREADS,
            download_root=whisper_settings.DOWNLOAD_ROOT,
        )
        logging.info("Model downloaded")

    async def transcribe_voice_message(self, message: Message) -> str:
        suffix = ".ogg"
        if message.video_note:
            suffix = ".mp4"

        async with (
            aiofiles.tempfile.NamedTemporaryFile(suffix=suffix) as input_voice,
            aiofiles.tempfile.NamedTemporaryFile(suffix=".wav") as output_voice,
        ):
            await message.download_media(file=input_voice.name)
            self.convert_ogg_to_wav(input_voice.name, output_voice.name)
            return self.get_transcribe(output_voice.name)

    def get_transcribe(self, voice: str) -> str:
        """raise Exception"""
        segments, _ = self.model.transcribe(
            audio=voice, vad_filter=True, beam_size=1, language="ru"
        )
        return "".join([segment.text.strip() for segment in segments]).strip()

    @classmethod
    def convert_ogg_to_wav(cls, ogg_file_path: str, wav_file_path: str) -> None:
        """raise Exception"""
        (ffmpeg.input(ogg_file_path).output(wav_file_path).run(overwrite_output=True))
