"""
Пример использования Google Gemini Whisper API для транскрипции аудио файлов.

Этот файл демонстрирует различные способы транскрипции аудио через Gemini API:
1. Прямая передача файла в модель через inline_data (для небольших файлов)
2. Загрузка файла через Files API и использование file_uri (для больших файлов)
"""

import asyncio
from pathlib import Path
from typing import BinaryIO

from google.genai import Client
from google.genai.types import Part


async def transcribe_audio_direct(
    client: Client,
    audio_file_path: str | Path,
    model_name: str = "gemini-2.0-flash-exp",
    language: str = "ru",
) -> str:
    """
    Транскрибирует аудио файл, передавая его напрямую в модель.

    Подходит для небольших файлов (обычно до 20MB).

    Args:
        client: Инициализированный клиент Google Gemini
        audio_file_path: Путь к аудио файлу
        model_name: Название модели Gemini (поддерживающей аудио)
        language: Язык транскрипции (например, "ru", "en")

    Returns:
        Транскрибированный текст
    """
    audio_path = Path(audio_file_path)

    # Определяем MIME тип на основе расширения файла
    mime_type_map = {
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".flac": "audio/flac",
    }
    mime_type = mime_type_map.get(audio_path.suffix.lower(), "audio/ogg")

    # Читаем файл
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    # Создаем Part с аудио данными используя inline_data (для байтов)
    audio_part = Part.from_bytes(data=audio_data, mime_type=mime_type)

    # Формируем промпт для транскрипции
    prompt = "Транскрибируй это аудио сообщение на русском языке. Верни только текст без дополнительных комментариев."

    # Вызываем модель через async API
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=[{"role": "user", "parts": [Part.from_text(text=prompt), audio_part]}],
    )

    return response.text


async def transcribe_audio_via_file_upload(
    client: Client,
    audio_file_path: str | Path,
    model_name: str = "gemini-2.0-flash-exp",
    language: str = "ru",
) -> str:
    """
    Транскрибирует аудио файл, предварительно загрузив его через Files API.

    Подходит для больших файлов (более 20MB).
    Файл загружается на серверы Google и используется через file_uri.

    Args:
        client: Инициализированный клиент Google Gemini
        audio_file_path: Путь к аудио файлу
        model_name: Название модели Gemini (поддерживающей аудио)
        language: Язык транскрипции (например, "ru", "en")

    Returns:
        Транскрибированный текст
    """
    audio_path = Path(audio_file_path)

    # Определяем MIME тип на основе расширения файла
    mime_type_map = {
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".flac": "audio/flac",
    }
    mime_type = mime_type_map.get(audio_path.suffix.lower(), "audio/ogg")

    # Загружаем файл через Files API
    print(f"Загрузка файла {audio_path.name}...")
    uploaded_file = await client.aio.files.upload(
        path=str(audio_path),
        mime_type=mime_type,
    )

    print(f"Файл загружен. URI: {uploaded_file.uri}")

    try:
        # Ждем пока файл будет обработан
        print("Ожидание обработки файла...")
        await client.aio.files.wait(uploaded_file.name)

        # Создаем Part с file_uri используя метод from_uri
        audio_part = Part.from_uri(file_uri=uploaded_file.uri, mime_type=mime_type)

        # Формируем промпт для транскрипции
        prompt = "Транскрибируй это аудио сообщение на русском языке. Верни только текст без дополнительных комментариев."

        # Вызываем модель через async API
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=[
                {"role": "user", "parts": [Part.from_text(text=prompt), audio_part]}
            ],
        )

        return response.text

    finally:
        # Удаляем загруженный файл после использования
        print(f"Удаление файла {uploaded_file.name}...")
        await client.aio.files.delete(uploaded_file.name)


async def transcribe_audio_from_bytes(
    client: Client,
    audio_bytes: bytes,
    mime_type: str = "audio/ogg",
    model_name: str = "gemini-2.0-flash-exp",
    language: str = "ru",
) -> str:
    """
    Транскрибирует аудио из байтов (например, из памяти).

    Полезно когда файл уже загружен в память и не нужно сохранять на диск.

    Args:
        client: Инициализированный клиент Google Gemini
        audio_bytes: Байты аудио файла
        mime_type: MIME тип аудио (например, "audio/ogg", "audio/wav")
        model_name: Название модели Gemini (поддерживающей аудио)
        language: Язык транскрипции (например, "ru", "en")

    Returns:
        Транскрибированный текст
    """
    # Создаем Part с аудио данными используя inline_data (для байтов)
    audio_part = Part.from_bytes(data=audio_bytes, mime_type=mime_type)

    # Формируем промпт для транскрипции
    prompt = "Транскрибируй это аудио сообщение на русском языке. Верни только текст без дополнительных комментариев."

    # Вызываем модель через async API
    response = await client.aio.models.generate_content(
        model=model_name,
        contents=[{"role": "user", "parts": [Part.from_text(text=prompt), audio_part]}],
    )

    return response.text


async def transcribe_audio_from_file_object(
    client: Client,
    audio_file: BinaryIO,
    mime_type: str = "audio/ogg",
    model_name: str = "gemini-2.0-flash-exp",
    language: str = "ru",
) -> str:
    """
    Транскрибирует аудио из файлового объекта (например, из NamedTemporaryFile).

    Args:
        client: Инициализированный клиент Google Gemini
        audio_file: Файловый объект с аудио данными
        mime_type: MIME тип аудио (например, "audio/ogg", "audio/wav")
        model_name: Название модели Gemini (поддерживающей аудио)
        language: Язык транскрипции (например, "ru", "en")

    Returns:
        Транскрибированный текст
    """
    # Читаем данные из файлового объекта
    audio_bytes = audio_file.read()

    return await transcribe_audio_from_bytes(
        client=client,
        audio_bytes=audio_bytes,
        mime_type=mime_type,
        model_name=model_name,
        language=language,
    )


# Пример использования
async def main():
    """Пример использования функций транскрипции."""

    # Инициализация клиента
    # API ключ можно получить из переменной окружения GOOGLE_API_KEY
    # или передать напрямую: Client(api_key="your-api-key")
    client = Client(api_key="your-api-key-here")

    # Пример 1: Прямая транскрипция файла (для небольших файлов)
    print("=== Пример 1: Прямая транскрипция ===")
    try:
        result = await transcribe_audio_direct(
            client=client,
            audio_file_path="path/to/audio.ogg",
            language="ru",
        )
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # Пример 2: Транскрипция через загрузку файла (для больших файлов)
    print("\n=== Пример 2: Транскрипция через загрузку ===")
    try:
        result = await transcribe_audio_via_file_upload(
            client=client,
            audio_file_path="path/to/large_audio.ogg",
            language="ru",
        )
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {e}")

    # Пример 3: Транскрипция из байтов
    print("\n=== Пример 3: Транскрипция из байтов ===")
    try:
        with open("path/to/audio.ogg", "rb") as f:
            audio_bytes = f.read()

        result = await transcribe_audio_from_bytes(
            client=client,
            audio_bytes=audio_bytes,
            mime_type="audio/ogg",
            language="ru",
        )
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
