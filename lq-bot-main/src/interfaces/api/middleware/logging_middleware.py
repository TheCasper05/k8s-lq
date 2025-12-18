import time

from fastapi import Request
from src.infrastructure.adapters.logging.structured_logger import StructuredLogger
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de todas las requests HTTP."""

    def __init__(self, app, logger: StructuredLogger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log de request entrante
        self.logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            endpoint=request.url.path,
            http_method=request.method,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=getattr(request.state, "correlation_id", None),
        )

        # Procesar request
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Log de response exitosa
            self.logger.success(
                f"Request completed: {request.method} {request.url.path}",
                endpoint=request.url.path,
                http_method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=getattr(request.state, "correlation_id", None),
            )

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log de error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exception=e,
                endpoint=request.url.path,
                http_method=request.method,
                duration_ms=duration_ms,
                request_id=getattr(request.state, "correlation_id", None),
            )

            raise
