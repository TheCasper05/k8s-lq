# Import all task modules to ensure they are registered with Celery
# This allows autodiscovery to find all tasks without side effects
from apps.tasks import institutions  # noqa: F401
from apps.tasks import scenarios  # noqa: F401
from apps.tasks import users  # noqa: F401

__all__ = [
    "institutions",
    "scenarios",
    "users",
]
