"""
Django settings module.

This module imports all configuration from modular files.
All settings are organized by category for better maintainability.
"""

from config.settings.base import *  # noqa: F403, F401
from config.settings.apps import *  # noqa: F403, F401
from config.settings.database import *  # noqa: F403, F401
from config.settings.celery import *  # noqa: F403, F401
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
