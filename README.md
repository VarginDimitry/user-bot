# User Bot

Telegram userbot with voice transcription (Whisper), GPT answers (Gemini), and Instagram media download.

## How to run in Docker

1. Clone the repository:
    ```bash
    git clone git@github.com:VarginDimitry/user-bot.git
    cd user-bot
    ```
2. Create the Docker network (once):
    ```bash
    docker network create usrbot-network
    ```
3. Create a `.env` file from the template:
    ```bash
    cp .env.example .env
    ```
    Fill in the values below (nested settings use `__` as delimiter).

    ### Telegram
    * `USER_BOT__API_ID` — Telegram API ID ([my.telegram.org](https://my.telegram.org))
    * `USER_BOT__API_HASH` — Telegram API hash ([my.telegram.org](https://my.telegram.org))
    * `USER_BOT__APP_NAME` — Telethon session name (default: `Telethon`)

    ### Logger
    * `LOGGER__BOT_TOKEN` — Telegram bot token used to send error logs
    * `LOGGER__ERROR_LOGGER_SEND_TO` — chat/user ID that receives error logs
    * `LOGGER__ENABLE_TELEGRAM` — enable Telegram error logging (default: `true`)

    ### Whisper (voice transcription)
    * `WHISPER__MODEL` — model name (e.g. `large-v3-turbo`)
    * `WHISPER__DEVICE` — device (e.g. `cpu`)
    * `WHISPER__COMPUTE_TYPE` — compute type (e.g. `int8`)
    * `WHISPER__CPU_THREADS` — CPU threads (e.g. `1`)
    * `WHISPER__DOWNLOAD_ROOT` — model download directory (e.g. `downloads/whisper`)
    * `WHISPER__BLACK_LIST` — chat IDs where auto-transcription is disabled (e.g. `[1, 2]`)
    * `WHISPER__WHITE_LIST` — chat IDs where auto-transcription is always enabled, including groups (e.g. `[1, 2]`)
    * `HF_TOKEN` - [Optional] Hugging Face API token ([Hugging Face](https://huggingface.co/settings/tokens))

    ### Gemini
    * `GEMINI__API_KEY` — Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

    ### OpenAI-compatible API (Cursor proxy in Compose)
    * `OPENAI__API_KEY` — API key (default: `cursor`)
    * `OPENAI__BASE_URL` — base URL (Docker: `http://cursor:3000/v1`, local: `http://localhost:3000/v1`)
    * `OPENAI__MODEL` — model name (default: `cursor-grok-4.5-low`)

    ### Instagram
    * `INSTAGRAM__BLACK_LIST` — chat IDs where Instagram download is disabled (e.g. `[1, 2]`)
    * `INSTAGRAM__DOWNLOAD_BOT_ID` — helper bot ID for downloads (optional)
    * `INSTAGRAM__DOWNLOAD_BOT_TIMEOUT` — download timeout in seconds (optional)

    ### Postgres
    * `POSTGRES__DNS` — SQLAlchemy async DSN  
      Docker: `postgresql+asyncpg://usrbot:usrbot@postgres:5432/usrbot`  
      Local: `postgresql+asyncpg://usrbot:usrbot@localhost:5131/usrbot`
    * `POSTGRES__ECHO` — SQLAlchemy echo (default: `true`)
    * `POSTGRES__MAX_POOL_SIZE` — pool size (default: `5`)

4. Build and run:
   1. First start (create Telethon session):  
      `docker compose up -d --build && docker attach user-bot`  
      then enter Telegram credentials when prompted
   2. Later starts:  
      `docker compose up -d --build`
   3. Skip rebuild:  
      `docker compose up -d`

## Commands

* `/help` — list bot capabilities
* `/transcribe` — reply to a voice/video note to transcribe it
* `/gpt <prompt>` — ask Gemini
* Send an Instagram link — download photo/video
* Voice / video notes in private chats (or chats from `WHISPER__WHITE_LIST`) are transcribed automatically
