"""
Test configuration settings.
Overrides settings for running tests with pytest.
"""

# Import base settings modules (but not celery to avoid dependency issues in tests)
from config.settings.base import *  # noqa: F403, F401
from config.settings.apps import *  # noqa: F403, F401
from config.settings.cache import *  # noqa: F403, F401
from config.settings.media_storage import *  # noqa: F403, F401
from config.settings.auth import *  # noqa: F403, F401
from config.settings.security import *  # noqa: F403, F401
from config.settings.logging import *  # noqa: F403, F401
from config.settings.templates import *  # noqa: F403, F401
from config.settings.internationalization import *  # noqa: F403, F401
from config.settings.resend import *  # noqa: F403, F401
from config.settings.third_party import *  # noqa: F403, F401
from config.settings.realtime_jwt import *  # noqa: F403, F401
from config.settings.user_model import *  # noqa: F403, F401

# NOTE: We do NOT import celery settings here to avoid celery/kombu dependency in tests

# Override database settings to use SQLite in-memory for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable database routers for tests
DATABASE_ROUTERS = []

# AWS/S3 settings for tests (required by PresignedURLService)
AWS_ACCESS_KEY_ID = "test-access-key-id"
AWS_SECRET_ACCESS_KEY = "test-secret-access-key"
AWS_STORAGE_BUCKET_NAME = "test-bucket"
AWS_S3_ENDPOINT_URL = "https://test.example.com"
AWS_LOCATION = "media"
DO_SPACES_PRESIGN_EXPIRE_SECONDS = 3600

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-test-cache",
    }
}

# Celery settings for tests - run tasks synchronously
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# Disable Sentry in tests
import sentry_sdk  # noqa: E402

sentry_sdk.init(dsn=None)
