"""
Security, CORS, and CSRF configuration.
"""

from config.settings.base import env
from corsheaders.defaults import default_headers

# CORS configuration
# Note: With JWT authentication, we don't need credentials (cookies) for API/GraphQL requests
# CORS_ALLOW_CREDENTIALS is kept for compatibility with Django admin session auth
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-session-token",
    "x-email-verification-key",
    "x-password-reset-key",
)

# CSRF configuration (only needed for Django admin and form-based views)
# GraphQL and API use JWT, which doesn't require CSRF protection
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Security settings (production)
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
SECURE_HSTS_SECONDS = env(
    "SECURE_HSTS_SECONDS"
)  # TODO: set this to 60 seconds first and then to 518400 once you prove the former works, # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
SECURE_HSTS_INCLUDE_SUBDOMAINS = env("SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = env("SECURE_HSTS_PRELOAD")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
