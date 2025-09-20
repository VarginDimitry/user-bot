FROM python:3.12.11-slim AS builder

ENV UV_SYSTEM_PYTHON=1
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --locked --no-install-project

###############################################
FROM python:3.12.11-slim

WORKDIR /app

ADD src .

COPY --from=builder /app/.venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app/.venv/bin/* /usr/local/bin/

CMD ["python", "/app/main.py"]
