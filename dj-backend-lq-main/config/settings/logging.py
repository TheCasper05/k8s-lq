"""
Logging configuration.
"""

from config.settings.base import LOG_DIR

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # 1️⃣  Formato único
    "formatters": {
        "verbose": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
    },
    # 2️⃣  Handlers
    "handlers": {
        # ----- archivo exclusivo para tareas Celery ------------------
        "tasks_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "tasks_errors.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "level": "ERROR",
            "formatter": "verbose",
        },
        # ----- catch-all para el resto de la app ---------------------
        "default_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app_errors.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "level": "ERROR",
            "formatter": "verbose",
        },
        # ----- consola en INFO+ --------------------------------------
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",  # <-- aquí el cambio clave
            "formatter": "verbose",
        },
    },
    # 3️⃣  Loggers
    "loggers": {
        # 3a)  Tareas Celery
        "lq.tasks": {  # usa este nombre en tus tasks
            "handlers": ["tasks_file", "console"],  # solo escribe en tasks_errors.log
            "level": "ERROR",  # permite .info(), .error() ...
            "propagate": False,  # sube al root → consola
        },
        # 3b)  Root (= todo lo demás)
        "": {
            "handlers": ["default_file", "console"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
