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
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8082

test:
	uv run pytest

lint:
	@ruff check . --fix
	exit 0

format:
	uv run ruff format .

qa: format lint test

check: lint test

gh-fix:
	@uv run ruff check . --output-format=github --fix

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

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

docker-build:
	docker build -t lq-realtime-service:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f ws-service

token:
	@python examples/generate_token.py --user-id test-user-123 --tenant-id test-tenant-456

help:
	@echo "LQ Real-time Service - Available Commands"
	@echo "=========================================="
	@echo ""
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'
	exit 0
