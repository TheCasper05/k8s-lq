import uuid

from fastapi import Request
from src.infrastructure.adapters.logging.structured_logger import correlation_id_var
from starlette.middleware.base import BaseHTTPMiddleware


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware para gestionar Correlation IDs en requests HTTP."""

    async def dispatch(self, request: Request, call_next):
        # Obtener o generar correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Establecer en ContextVar
        correlation_id_var.set(correlation_id)

        # Agregar al state del request para acceso fácil
        request.state.correlation_id = correlation_id

        # Procesar request
        response = await call_next(request)

        # Agregar correlation ID a response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
