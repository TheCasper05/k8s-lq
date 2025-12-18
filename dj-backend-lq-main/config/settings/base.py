"""
Base configuration settings.
Contains core Django settings, paths, and environment variables.
"""

import os
import sys
from pathlib import Path
import environ
from .sentry import initialize_sentry

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# Environment variables
env = environ.Env(
    ENVIRONMENT=(str, "local"),  # local, development, staging, production
    DEBUG=(bool, False),
    NPLUSONE_RAISE=(bool, False),
    SECRET_KEY=(str, None),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR}/db.sqlite3"),
    REPLICA_DB_URL=(str, ""),
    STATIC_ROOT=(str, "static/"),
    STATIC_URL=(str, "/static/"),
    MEDIA_URL=(str, "/media/"),
    MEDIA_ROOT=(str, "media/"),
    STORAGES_DEFAULT_BACKEND=(str, "django.core.files.storage.FileSystemStorage"),
    ENDPOINT_URL_FRONTEND_ST=(str, "http://localhost:3000"),
    ENDPOINT_URL_FRONTEND_ADMIN=(str, "http://localhost:3001"),
    GOOGLE_CLIENT_ID=(str, "your-google-client-id"),
    GOOGLE_SECRET=(str, "your-google-secret"),
    EMAIL_URL=(str, "consolemail://user:password@localhost:25"),
    HEADLESS_SERVE_SPECIFICATION=(bool, True),
    CORS_ALLOWED_ORIGINS=(
        list,
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://0.0.0.0:3001",
        ],
    ),
    CSRF_TRUSTED_ORIGINS=(
        list,
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://0.0.0.0:3001",
        ],
    ),
    # Security settings (production only)
    SECURE_SSL_REDIRECT=(bool, False),
    SECURE_HSTS_SECONDS=(int, 0),
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, False),
    SECURE_HSTS_PRELOAD=(bool, False),
    LINGOBOT_ADDRESS=(str, "http://localhost:8001"),
    REDIS_URL=(str, "redis://localhost:6379/0"),
    REDIS_CACHE_URL=(str, "redis://localhost:6379/1"),
    AWS_ACCESS_KEY_ID=(str, ""),
    AWS_SECRET_ACCESS_KEY=(str, ""),
    AWS_STORAGE_BUCKET_NAME=(str, ""),
    AWS_DEFAULT_ACL=(str, ""),
    AWS_S3_ENDPOINT_URL=(str, ""),
    MICROSOFT_CLIENT_ID=(str, "your-microsoft-client-id"),
    MICROSOFT_SECRET=(str, "your-microsoft-secret"),
    CELERY_BROKER_USE_SSL=(dict, None),
    CELERY_REDIS_BACKEND_USE_SSL=(dict, None),
    UNSPLASH_URL=(str, "https://api.unsplash.com"),
    UNSPLASH_API_KEY=(str, "your.unsplash.api.key"),
    WEBHOOK_VERIFY_TOKEN=(str, "your-webhook-verify-token"),
    GRAPH_API_TOKEN=(str, "your-whatsapp-graph-api-token"),
    PHONE_NUMBER_ID=(str, "your-whatsapp-phone-number-id"),
    PRONUNCIATION_API_KEY=(str, "your-pronunciation-api-key"),
    SENTRY_DNS=(str, "your-sentry-dns"),
    LINGOBOT_API_KEY=(str, "your-lingobot-api-key"),
    DO_SPACES_PRESIGN_EXPIRE_SECONDS=(int, 3600),
)

# Read .env file if it exists (local development)
# In production, env vars are set by the platform (DigitalOcean, etc.)
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# Environment configuration
ENVIRONMENT = env("ENVIRONMENT")

# Initialize Sentry
initialize_sentry(dsn=env("SENTRY_DNS"), environment=ENVIRONMENT)

# Core Django settings
SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY:
    if ENVIRONMENT == "local":
        SECRET_KEY = "dev-secret-key"
    else:
        raise ValueError("SECRET_KEY environment variable must be set")

DEBUG = env("DEBUG")
NPLUSONE_RAISE = env("NPLUSONE_RAISE")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
LINGOBOT_API_KEY = env("LINGOBOT_API_KEY")
UNSPLASH_URL = env("UNSPLASH_URL")
LINGOBOT_ADDRESS = env("LINGOBOT_ADDRESS")

SITE_ID = 1

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Data upload limits
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

# WhatsApp configuration
WEBHOOK_VERIFY_TOKEN = env("WEBHOOK_VERIFY_TOKEN")
GRAPH_API_TOKEN = env("GRAPH_API_TOKEN")
PHONE_NUMBER_ID = env("PHONE_NUMBER_ID")
PRONUNCIATION_API_KEY = env("PRONUNCIATION_API_KEY")
