ifneq (,$(wildcard ./.env))
    include .env
    export
endif

PYTHON_SRC := src

ruff-lint:
	poetry run ruff check ${PYTHON_SRC} --fix

ruff-format:
	poetry run isort .
	poetry run ruff format ${PYTHON_SRC}

mypy:
	@poetry run mypy ${PYTHON_SRC} --no-color-output --explicit-package-bases

check:
	make ruff-format
	make ruff-lint
	make mypy