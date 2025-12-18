"""
Celery configuration.

This file configures Celery with multiple queues for horizontal scaling:
- high_priority: Critical/urgent tasks (user-facing operations)
- default: General purpose tasks
- low_priority: Background/batch tasks (reports, cleanup, etc.)
"""

from datetime import timedelta
from config.settings.base import env
from libs.utils.main import cast_ssl_verify_mode
from kombu import Queue, Exchange

# ===================================================
# Broker & Backend Configuration
# ===================================================
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = env("REDIS_URL")
CELERY_CACHE_URL = env("REDIS_CACHE_URL")

CELERY_BROKER_USE_SSL = env.dict(
    "CELERY_BROKER_USE_SSL",
    cast={"value": cast_ssl_verify_mode},
    default=None,
)

CELERY_REDIS_BACKEND_USE_SSL = env.dict(
    "CELERY_REDIS_BACKEND_USE_SSL",
    cast={"value": cast_ssl_verify_mode},
    default=None,
)

# ===================================================
# Serialization & Timezone
# ===================================================
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Bogota"
CELERY_ENABLE_UTC = True

# ===================================================
# Broker Connection & Reliability
# ===================================================
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10

# ===================================================
# Worker Configuration
# ===================================================
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Solo toma 1 tarea a la vez
CELERYD_MAX_TASKS_PER_CHILD = 100  # Recicla worker cada 100 tareas
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# ===================================================
# Task Execution & Results
# ===================================================
CELERY_IGNORE_RESULT = True  # No guardar resultados por defecto
CELERY_TASK_IGNORE_RESULT = True  # Excepto tareas específicas
CELERY_RESULT_EXPIRES = 3600  # Resultados expiran en 1 hora
CELERY_TASK_TRACK_STARTED = True  # Track cuando una tarea inicia
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutos timeout hard
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutos timeout soft

# ===================================================
# Queues Configuration
# ===================================================
# Exchange por defecto
default_exchange = Exchange("default", type="direct")

CELERY_TASK_QUEUES = (
    # Cola de alta prioridad - Tareas críticas/urgentes
    Queue(
        "high_priority",
        exchange=default_exchange,
        routing_key="high_priority",
        priority=10,
    ),
    # Cola por defecto - Tareas generales
    Queue(
        "default",
        exchange=default_exchange,
        routing_key="default",
        priority=5,
    ),
    # Cola de baja prioridad - Tareas lentas/batch
    Queue(
        "low_priority",
        exchange=default_exchange,
        routing_key="low_priority",
        priority=1,
    ),
)

# Cola por defecto si no se especifica
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_DEFAULT_EXCHANGE = "default"
CELERY_TASK_DEFAULT_ROUTING_KEY = "default"

# ===================================================
# Task Routing
# ===================================================
# Definir qué tareas van a qué colas
CELERY_TASK_ROUTES = {
    # High Priority - Tareas urgentes/críticas
    "apps.tasks.users.send_welcome_email": {"queue": "high_priority"},
    "apps.tasks.users.send_password_reset": {"queue": "high_priority"},
    # Default - Tareas generales
    "apps.tasks.institutions.*": {"queue": "default"},
    "apps.tasks.scenarios.*": {"queue": "default"},
    # Low Priority - Tareas batch/background
    "apps.tasks.users.cleanup_inactive_users": {"queue": "low_priority"},
}

# ===================================================
# Beat Schedule - Tareas Periódicas
# ===================================================
CELERY_BEAT_SCHEDULE = {
    # Snapshot semanal
    "take_snapshot": {
        "task": "core.tasks.take_snapshot",
        "schedule": timedelta(days=7),
        "options": {"queue": "low_priority"},
    },
    # Ejemplo: Cleanup diario
    # "cleanup_inactive_users": {
    #     "task": "apps.tasks.users.cleanup_inactive_users",
    #     "schedule": timedelta(days=1),
    #     "options": {"queue": "low_priority"},
    # },
}

# ===================================================
# Monitoring & Logging
# ===================================================
CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TASK_SEND_SENT_EVENT = True
