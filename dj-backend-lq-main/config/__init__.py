# Import celery app, but make it optional for testing environments
try:
    from celery import app as celery_app

    __all__ = ("celery_app",)
except ImportError:
    # Celery is not installed (e.g., in test environment)
    celery_app = None
    __all__ = tuple()
