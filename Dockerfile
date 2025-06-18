FROM python:3.13.3-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

RUN poetry install --only main --no-interaction --no-ansi

COPY src .

FROM python:3.13.3-slim

WORKDIR /app
USER app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg libavcodec-extra

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder --chown=app:app /app /app

# Set entrypoint
CMD ["python", "main.py"]