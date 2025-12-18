# Multi-stage Dockerfile for LingoBot FastAPI application
# Stage 1: Builder - Install dependencies using uv
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv /app/.venv && \
    uv pip install --no-cache-dir -r pyproject.toml

# Stage 2: Runtime - Minimal image with only runtime dependencies
FROM python:3.14-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/
COPY --chown=appuser:appuser pyproject.toml /app/

# Set Python path
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run the application
CMD ["uvicorn", "interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8081"]
