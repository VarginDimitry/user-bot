ifneq (,$(wildcard ./.env))
    include .env
    export
endif

PYTHON_SRC := src

ruff-lint:
	uv run ruff check ${PYTHON_SRC} --fix

ruff-format:
	uv run isort .
	uv run ruff format ${PYTHON_SRC}

mypy:
	@uv run mypy ${PYTHON_SRC} --no-color-output --explicit-package-bases

check:
	make ruff-format
	make ruff-lint
	make mypy