"""
Authentication and AllAuth configuration.
"""

from config.settings.base import env


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = True
# ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
HEADLESS_SERVE_SPECIFICATION = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "username",
    "password1*",
    "password2*",
    "first_name",
    "last_name",
]

ACCOUNT_EMAIL_VERIFICATION = "mandatory"

ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"

# Render HTML templates for account emails
ACCOUNT_TEMPLATE_EXTENSION = "html"

# Use custom adapter to send HTML emails
ACCOUNT_ADAPTER = "config.adapters.HTMLEmailAdapter"

CORS_ALLOW_CREDENTIALS = True
HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": f"{env('ENDPOINT_URL_FRONTEND_ST')}/auth/verify-email?key={{key}}",
    "account_reset_password": f"{env('ENDPOINT_URL_FRONTEND_ST')}/auth/password/reset",
    "account_reset_password_from_key": f"{env('ENDPOINT_URL_FRONTEND_ST')}/auth/password/reset/key/{{key}}",
    "account_signup": f"{env('ENDPOINT_URL_FRONTEND_ST')}/auth/register",
    "socialaccount_login_error": f"{env('ENDPOINT_URL_FRONTEND_ST')}/auth/provider/callback",
}
HEADLESS_CLIENTS = ("browser", "app")
HEADLESS_SERVE_SPECIFICATION = env("HEADLESS_SERVE_SPECIFICATION")
HEADLESS_SPECIFICATION_TEMPLATE_NAME = "headless/spec/swagger_cdn.html"

# Note: JWT tokens are handled by custom views (authentication.views.*)
# that override the default allauth headless endpoints

SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# Social providers configuration
# Note: APP credentials are managed in the database via SocialApp model
# Use management command: python manage.py setup_social_apps
# Or configure in Django admin: /admin/socialaccount/socialapp/
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "EMAIL_AUTHENTICATION": True,
        "SCOPE": [
            "profile",
            "email",
        ],
    },
    "microsoft": {
        "TENANT": "common",
    },
}

# Environment variables for management command
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = env("GOOGLE_SECRET")
MICROSOFT_CLIENT_ID = env("MICROSOFT_CLIENT_ID")
MICROSOFT_SECRET = env("MICROSOFT_SECRET")
