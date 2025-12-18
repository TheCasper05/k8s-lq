"""
Email configuration.
"""

from config.settings.base import env

# Check if we should use Resend API instead of SMTP
USE_RESEND_API = env.bool("USE_RESEND_API", default=False)

if USE_RESEND_API:
    # Use Resend HTTP API (bypasses SMTP port blocking)
    EMAIL_BACKEND = "config.email_backend.ResendAPIBackend"
    RESEND_API_KEY = env("RESEND_API_KEY")
    DEFAULT_FROM_EMAIL = "support@lingoquesto.com"
else:
    # Use traditional SMTP (requires open SMTP ports)
    EMAIL_CONFIG = env.email("EMAIL_URL")
    DEFAULT_FROM_EMAIL = "support@lingoquesto.com"
    vars().update(EMAIL_CONFIG)
