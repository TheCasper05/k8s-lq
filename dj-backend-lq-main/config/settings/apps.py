"""
Django apps and middleware configuration.
"""

from config.settings.base import NPLUSONE_RAISE, ENVIRONMENT

# Django apps
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "storages",
]

# Third-party apps
THIRD_PARTY_APPS: list[str] = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "django.contrib.admin",
    "corsheaders",
    "nested_admin",
    "graphene_django",
    "allauth",
    "allauth.account",
    "allauth.headless",
    # 'allauth.usersessions'
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.dummy",
    "django_json_widget",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    # "django_extensions",
]

# Local apps
LOCAL_APPS: list[str] = ["authentication", "core", "files", "tasks", "activities"]

HEADLESS_ADAPTER = "allauth.headless.adapter.DefaultHeadlessAdapter"
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.core.middlewares.PerformanceLoggingMiddleware",
    "django_currentuser.middleware.ThreadLocalUserMiddleware",
]

# Add WhiteNoise middleware for staging to serve static files
if ENVIRONMENT == "staging":
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Add zeal middleware if NPLUSONE_RAISE is enabled
if NPLUSONE_RAISE:
    INSTALLED_APPS.append("zeal")
    MIDDLEWARE.append("zeal.middleware.zeal_middleware")
