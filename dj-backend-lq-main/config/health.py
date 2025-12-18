"""Health check views for monitoring and deployment verification."""

import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint for load balancers and monitoring systems.
    Returns 200 if all services are operational, 503 otherwise.
    """
    status = {"status": "healthy", "services": {}}
    http_status = 200

    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["services"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status["services"]["database"] = "unhealthy"
        status["status"] = "unhealthy"
        http_status = 503

    # Check Redis/Cache connectivity
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            status["services"]["cache"] = "healthy"
        else:
            raise Exception("Cache get/set failed")
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        status["services"]["cache"] = "unhealthy"
        status["status"] = "unhealthy"
        http_status = 503

    return JsonResponse(status, status=http_status)


def readiness_check(request):
    """
    Readiness check endpoint - indicates if the application is ready to serve traffic.
    """
    return JsonResponse(
        {"status": "ready", "environment": getattr(settings, "ENVIRONMENT", "unknown")}
    )


def liveness_check(request):
    """
    Liveness check endpoint - indicates if the application is alive.
    Simple check that doesn't depend on external services.
    """
    return JsonResponse({"status": "alive"})
