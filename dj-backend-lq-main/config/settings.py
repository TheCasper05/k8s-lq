"""
Django settings module.

This file imports all settings from the modular configuration files
located in config/settings/ directory.

For maintainability, settings are organized by category:
- base.py: Core Django settings, paths, environment variables
- apps.py: INSTALLED_APPS and MIDDLEWARE
- database.py: Database configuration
- celery.py: Celery configuration
- cache.py: Cache configuration
- media_storage.py: Media files and storage
- auth.py: Authentication and AllAuth
- security.py: Security, CORS, CSRF
- logging.py: Logging configuration
- templates.py: Templates configuration
- internationalization.py: i18n and l10n
- email.py: Email configuration
- third_party.py: Third-party integrations (Graphene, REST Framework, Unfold)
"""

# Import all settings from modular files
from config.settings import *  # noqa: F403, F401
