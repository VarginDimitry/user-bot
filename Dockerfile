FROM python:3.12.11-slim AS builder

WORKDIR /packages

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

FROM python:3.12.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg libavcodec-extra

COPY --from=builder /packages/.venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src /app

# Set entrypoint
CMD ["python", "main.py"]
