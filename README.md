# User Bot
## How to run in Docker

1. Clone the repository:
    ```bash
    git clone git@github.com:VarginDimitry/user-bot.git
    cd user-bot
    ```
2. Create a `.env` file with the following parameters:
    * `API_ID` - Telegram API ID (get from [my.telegram.org](https://my.telegram.org))
    * `API_HASH` - Telegram API hash (get from [my.telegram.org](https://my.telegram.org))
    * `PHONE` - Telegram phone number
    * `LOGIN` - Telegram login
    * `WHISPER_MODEL` - Whisper model to use (for example, `large-v3-turbo`)
    * `WHISPER_DEVICE` - device to use for Whisper (for example, `cpu`)
    * `WHISPER_COMPUTE_TYPE` - compute type to use for Whisper (for example, `int8`)
    * `WHISPER_CPU_THREADS` - number of CPU threads to use for Whisper (for example, `1`)
    * `WHISPER_DOWNLOAD_ROOT` - directory to download Whisper models to (for example, `downloads/whisper`)
3. Build the Docker image:
    ```bash
    docker compose build
    ```
4. Run the Docker container for creating a session:
   1. ```docker compose up```
   2. Input verification code and password
   3. ```docker compose down```
5. Run the Docker container:
   ```bash
   docker compose up -d
   ```