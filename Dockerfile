FROM python:3.12.9-slim-bullseye

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PATH="$PATH:/root/.poetry/bin"

# Installation dependency:
RUN pip install --upgrade pip && \
    pip install poetry && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copy only requirements, to cache them in docker layer
COPY ./poetry.lock ./pyproject.toml ./

# Project initialization:
RUN poetry install --no-interaction --no-ansi

COPY ./src .

CMD ["python", "main.py"]
