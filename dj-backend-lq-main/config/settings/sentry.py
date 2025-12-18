"""
Configuración optimizada de Sentry para entornos de producción con auto-escalado.

Esta configuración incluye:
- Muestreo inteligente para reducir costos
- Integración con Django, Celery y Redis
- Perfilado de rendimiento para identificar cuellos de botella
- Filtrado de ruido (health checks, WebSocket disconnects)
- Contexto de entorno y releases
"""

import os
import logging
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def traces_sampler(sampling_context):
    """
    Control inteligente de muestreo para auto-escalado.
    Reduce costos filtrando ruido y ajustando por tipo de operación.

    Retorna un float entre 0.0 (nunca muestrear) y 1.0 (siempre muestrear).
    """
    asgi_scope = sampling_context.get("asgi_scope", {})
    path_info = asgi_scope.get("path", "")

    if path_info in ["/health", "/health/", "/health/db/"]:
        return 0.0

    transaction_context = sampling_context.get("transaction_context", {})
    transaction_name = transaction_context.get("name", "")

    if "introspection" in transaction_name.lower() or "__schema" in transaction_name:
        return 0.01

    critical_operations = ["payment", "grading", "evaluation", "billing"]
    if any(op in transaction_name.lower() for op in critical_operations):
        return 1.0

    if "mutation" in transaction_name.lower():
        return 0.5

    if "query" in transaction_name.lower():
        return 0.2

    return 1.0


def profiles_sampler(sampling_context):
    """
    Perfilado de CPU para identificar cuellos de botella.
    Más conservador que traces debido al overhead y costo.

    El perfilado captura stack traces continuos para identificar
    qué funciones consumen más CPU.
    """
    asgi_scope = sampling_context.get("asgi_scope", {})
    path_info = asgi_scope.get("path", "")

    if path_info in ["/health", "/health/", "/health/db/"]:
        return 0.0

    return 0.05


def before_send(event, hint):
    """
    Filtra eventos antes de enviarlos a Sentry.
    Retorna None para descartar el evento, o el evento modificado para enviarlo.
    """
    exceptions = event.get("exception", {}).get("values", [])

    for exc in exceptions:
        exc_type = exc.get("type", "")
        exc_value = exc.get("value", "")

        if "WebSocket" in exc_type and any(
            term in exc_value.lower()
            for term in ["disconnect", "closed", "connection lost"]
        ):
            return None

        if exc_type in [
            # "ClientDisconnected",
            "BrokenPipeError",
            "ConnectionResetError",
        ]:
            return None

        if "TimeoutError" in exc_type and "connection" in exc_value.lower():
            return None

        if exc_type == "PermissionError" and "/static/" in exc_value:
            return None

    if "request" in event:
        request = event["request"]

        if request.get("url", "").endswith("/graphql/"):
            pass

    return event


def initialize_sentry(dsn: str, environment: str = "local"):
    """
    Inicializa Sentry con configuración optimizada para producción.

    Args:
        dsn: El DSN de Sentry
        environment: Entorno de ejecución (local, development, qa, staging, production)
        debug: Si está en modo debug (development)
    """
    if not dsn or dsn == "your-sentry-dns":
        print(
            f"Sentry not initialized (no DSN configured) - environment: {environment}"
        )
        return

    valid_environments = ["local", "development", "staging", "production"]
    if environment not in valid_environments:
        print(
            f"Warning: Invalid environment '{environment}'. Using 'local' as default."
        )
        environment = "local"

    release = f"back-lq-v2@{os.getenv('GIT_COMMIT', 'unknown')}"

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
                signals_spans=True,
                cache_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sampler=traces_sampler,
        profiles_sampler=profiles_sampler,
        send_default_pii=True,
        attach_stacktrace=True,
        max_breadcrumbs=50,
        before_send=before_send,
        _experiments={
            "continuous_profiling_auto_start": False,
        },
        shutdown_timeout=2,
    )

    print(
        f"✓ Sentry initialized for environment '{environment}' with release {release}"
    )
