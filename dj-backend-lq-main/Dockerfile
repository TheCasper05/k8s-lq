FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    pkg-config \
    netcat-openbsd \
    cmake \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY ./docker ./docker
RUN chmod +x ./docker/entrypoint.sh

COPY . .

RUN mkdir -p logs

EXPOSE 8000

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["server"]
