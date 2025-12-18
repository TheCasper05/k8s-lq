"""
Media files and storage configuration.
"""

from config.settings.base import env, ENVIRONMENT

# Static files
STATIC_ROOT = env("STATIC_ROOT")
STATIC_URL = env("STATIC_URL")

# Media files and AWS S3 configuration
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "media"
AWS_DEFAULT_ACL = env("AWS_DEFAULT_ACL")
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

# Configure storage backends
# Use WhiteNoise for static files in staging to serve them efficiently with DEBUG=False
STORAGES = {
    "default": {"BACKEND": env("STORAGES_DEFAULT_BACKEND")},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if ENVIRONMENT == "staging"
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

MEDIA_URL = env("MEDIA_URL")
MEDIA_ROOT = env("MEDIA_ROOT")

DO_SPACES_PRESIGN_EXPIRE_SECONDS = env("DO_SPACES_PRESIGN_EXPIRE_SECONDS")
