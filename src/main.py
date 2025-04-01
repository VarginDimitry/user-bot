import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from composite_container import voice_service, bot


@bot.on_message(filters.voice | filters.video_note | filters.private)
async def transcribe_voices(client: Client, message: Message):
    result = await voice_service.transcribe_voice_message(message)
    await message.reply(
        text=f"Расшифровка:\n\n{result}",
        quote=True
    )

if __name__ == '__main__':
    bot.run()