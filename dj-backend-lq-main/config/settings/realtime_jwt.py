"""
Realtime JWT configuration for lq-realtime-service authentication.

This configuration handles JWT tokens specifically designed for authenticating
frontend connections to the realtime service. These tokens are separate from
the main session JWT tokens and have a shorter expiration time.
"""

import os
from django.core.exceptions import ImproperlyConfigured
from config.settings.base import ENVIRONMENT


def get_multiline_env(key, default=None):
    """
    Get environment variable and replace \\n with actual newlines.

    This allows RSA keys to be stored in .env files as:
    REALTIME_JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAI...\n-----END PRIVATE KEY-----"
    """
    value = os.environ.get(key, default)
    if value:
        # Replace literal \n with actual newlines
        return value.replace("\\n", "\n")
    return value


# Realtime JWT Private Key (RSA or EC)
# This should be set as an environment variable
# Example format for RSA (use \n for line breaks in .env):
# REALTIME_JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAI...\n-----END PRIVATE KEY-----"
REALTIME_JWT_PRIVATE_KEY = get_multiline_env("REALTIME_JWT_PRIVATE_KEY")

# Realtime JWT Public Key (for verification - optional, mainly for testing)
# The actual verification should happen in lq-realtime-service
REALTIME_JWT_PUBLIC_KEY = get_multiline_env("REALTIME_JWT_PUBLIC_KEY")

# JWT Algorithm (RS256, RS384, RS512, ES256, ES384, ES512)
# RS256 (RSA with SHA-256) is recommended
REALTIME_JWT_ALGORITHM = os.environ.get("REALTIME_JWT_ALGORITHM", "RS256")

# Token expiration time in minutes (default: 10 minutes)
# This is intentionally short for security
REALTIME_JWT_EXPIRATION_MINUTES = int(
    os.environ.get("REALTIME_JWT_EXPIRATION_MINUTES", 10)
)

# Validation: Ensure required configuration is present in production
if ENVIRONMENT in ["production", "staging"]:
    if not REALTIME_JWT_PRIVATE_KEY:
        raise ImproperlyConfigured(
            "REALTIME_JWT_PRIVATE_KEY must be set in production/staging environments. "
            "This is required for signing realtime JWT tokens."
        )

# Development warning
if ENVIRONMENT == "local" and not REALTIME_JWT_PRIVATE_KEY:
    import warnings

    warnings.warn(
        "REALTIME_JWT_PRIVATE_KEY is not set. Realtime token generation will fail. "
        "Please configure this environment variable for development.",
        RuntimeWarning,
    )
