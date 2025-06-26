ifneq (,$(wildcard ./.env))
    include .env
    export
endif

PYTHON_SRC := src

ruff-lint:
	uvx ruff check ${PYTHON_SRC} --fix

ruff-format:
	uvx isort .
	uvx ruff format ${PYTHON_SRC}

mypy:
	@uvx mypy ${PYTHON_SRC} --no-color-output --explicit-package-bases

check:
	make ruff-format
	make ruff-lint
	#make mypy