"""
Main FastAPI application.
Configures routes, middleware, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import (
    BackgroundTasks,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    WebSocket,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import verify_system_api_key
from app.config import get_settings
from app.redis_client import redis_client
from app.schemas import (
    ErrorResponse,
    GlobalBroadcastRequest,
    GlobalBroadcastResponse,
    HealthCheckResponse,
    MetricsResponse,
    WebhookProvider,
    WSMessage,
)
from app.utils.logging import setup_logging
from app.utils.metrics import metrics_collector
from app.webhooks import handle_webhook, webhook_registry
from app.websocket_handler import connection_manager, websocket_endpoint

settings = get_settings()

setup_logging(level=settings.log_level, format_type=settings.log_format)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    try:
        await redis_client.connect()
        logger.info("Redis connection established")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

    yield

    logger.info("Shutting down application...")

    try:
        await redis_client.disconnect()
        logger.info("Redis connection closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time WebSocket and Webhook service for LingoQuesto",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests."""
    logger.info(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"{request.method} {request.url.path} - Error: {e}")
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_response = ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred",
        detail={"error": str(exc)} if settings.debug else None,
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled",
    }


@app.get(settings.health_check_path, response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    Returns service status and basic metrics.
    """
    redis_connected = await redis_client.is_connected()
    stats = connection_manager.get_stats()

    return HealthCheckResponse(
        status="healthy" if redis_connected else "degraded",
        version=settings.app_version,
        redis_connected=redis_connected,
        active_connections=stats["active_connections"],
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """
    Metrics endpoint.
    Returns detailed application metrics.
    """
    if not settings.metrics_enabled:
        return JSONResponse(
            status_code=404,
            content={"error": "Metrics endpoint disabled"},
        )

    stats = connection_manager.get_stats()
    webhook_stats = webhook_registry.get_stats()
    system_metrics = metrics_collector.get_metrics()

    return MetricsResponse(
        active_websocket_connections=stats["active_connections"],
        total_messages_sent=stats["total_messages_sent"],
        total_messages_received=stats["total_messages_received"],
        total_webhooks_processed=webhook_stats["total_processed"],
        redis_pubsub_channels=stats["subscribed_channels"],
        uptime_seconds=system_metrics["uptime_seconds"],
        memory_usage_mb=system_metrics["memory_usage_mb"],
    )


@app.websocket("/ws")
async def websocket_route(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
):
    """
    WebSocket endpoint.
    Authenticates and manages WebSocket connections.

    Args:
        websocket: WebSocket connection
        token: JWT token for authentication
    """
    await websocket_endpoint(websocket, token)


@app.post("/webhooks/{provider}")
async def webhook_route(
    provider: WebhookProvider,
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str = Header(None, alias="x-signature"),
    x_tenant_id: str = Header(None, alias="x-tenant-id"),
):
    """
    Webhook endpoint for external providers.

    Args:
        provider: Webhook provider (stripe, github, slack, etc.)
        request: FastAPI request object
        background_tasks: Background task manager
        x_signature: Webhook signature header
        x_tenant_id: Optional tenant ID header

    Returns:
        Acceptance response
    """
    return await handle_webhook(
        provider=provider,
        request=request,
        background_tasks=background_tasks,
        x_signature=x_signature,
        x_tenant_id=x_tenant_id,
    )


@app.get("/debug/connections")
async def debug_connections():
    """
    Debug endpoint to view active connections.
    Only available in debug mode.
    """
    if not settings.debug:
        return JSONResponse(
            status_code=404,
            content={"error": "Debug endpoint disabled"},
        )

    stats = connection_manager.get_stats()
    connection_details = [
        {
            "connection_id": info.connection_id,
            "user_id": info.user_id,
            "tenant_id": info.tenant_id,
            "connected_at": info.connected_at.isoformat(),
            "last_activity": info.last_activity.isoformat(),
        }
        for info in connection_manager.connection_info.values()
    ]

    return {
        "stats": stats,
        "connections": connection_details,
    }


@app.post("/api/broadcast/global", response_model=GlobalBroadcastResponse)
async def global_broadcast(
    request: GlobalBroadcastRequest,
    x_api_key: str = Header(..., alias="x-api-key", description="System API key"),
):
    """
    Global broadcast endpoint for system-level messages.
    Sends a message to ALL connected users across all tenants.

    **Security**: Requires system API key in X-API-Key header.
    This endpoint is intended for admin panel use only.

    Args:
        request: Broadcast request with message type and payload
        x_api_key: System API key for authentication

    Returns:
        GlobalBroadcastResponse with broadcast status

    Example:
        ```bash
        curl -X POST http://localhost:8082/api/broadcast/global \\
          -H "Content-Type: application/json" \\
          -H "X-API-Key: your-system-api-key" \\
          -d '{
            "message_type": "system",
            "payload": {
              "title": "Maintenance Notice",
              "message": "System will be down for maintenance in 10 minutes",
              "priority": "high"
            }
          }'
        ```
    """
    # Verify system API key
    await verify_system_api_key(x_api_key)

    try:
        # Create WebSocket message
        ws_message = WSMessage(
            type=request.message_type,
            payload=request.payload,
            from_user=request.from_user or "system",
        )

        # Broadcast to all users globally
        subscribers_reached = await connection_manager.broadcast_global(ws_message)

        logger.info(
            f"Global broadcast sent: type={request.message_type}, subscribers={subscribers_reached}"
        )

        return GlobalBroadcastResponse(
            success=True,
            message="Global broadcast sent successfully",
            subscribers_reached=subscribers_reached,
        )

    except Exception as e:
        logger.error(f"Failed to send global broadcast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send broadcast: {e!s}",
        ) from e


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.app_name} on {settings.host}:{settings.port}")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
