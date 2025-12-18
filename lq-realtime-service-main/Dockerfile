FROM python:3.12-slim AS builder

WORKDIR /build

ENV PATH="/root/.local/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN /root/.local/bin/uv sync --frozen --no-dev && \
    ls -la /build/.venv/bin/ && \
    /build/.venv/bin/python --version

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/.venv /app/.venv

RUN find /app/.venv/bin -type f -exec sed -i 's|#!/build/.venv/bin/python|#!/app/.venv/bin/python|g' {} \; && \
    ls -la /app/.venv/bin/ && \
    test -f /app/.venv/bin/uvicorn || (echo "ERROR: uvicorn not found!" && exit 1)

COPY app/ ./app/

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8082/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--workers", "1"]
