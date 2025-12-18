"""
Internationalization and localization configuration.
"""

from config.settings.base import BASE_DIR

LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = False
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("de", "Deutsch"),
    ("ar", "العربية"),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "America/Bogota"
USE_TZ = True
