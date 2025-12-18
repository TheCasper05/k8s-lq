.PHONY: init run test lint format check

.DEFAULT_GOAL := help

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

init:
	uv venv
	uv sync --all-extras --group dev

sync:
	@echo "Running uv sync with environment variables from .env..."
	@uv sync --all-packages
	exit 0

run:
	uv run uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

# test:
# 	uv run pytest

test:
	uv run pytest --cov=src --cov-report=term-missing 

lint:
	@ruff check . --fix
	exit 0


format:
	uv run ruff format .

qa: format lint test

check: lint test

gh-fix:
	@uv run ruff check . --output-format=github --fix

dev: qa run

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf .venv
	@echo "Cleaned up cache and temporary files"
	exit 0

reset-venv:
	make clean
	@uv cache clean
	@uv sync --all-packages
	@echo "Virtual environment has been reset and dependencies installed."
	exit 0

help:
	@echo "LQ BOT - Available commands:"
	@echo ""
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'
	exit 0