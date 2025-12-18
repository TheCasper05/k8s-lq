"""
Services module for authentication app.

This module contains business logic services separated from models
to maintain clean architecture and separation of concerns.

ARCHITECTURE & IMPORT RULES:
============================

To avoid circular import issues, follow these architectural rules:

1. MODELS (models.py):
   - Can import: enums, core models, Django models
   - CANNOT import services at module level
   - CAN import services lazily (inside methods) when needed
   - Example: `def clean(self): from .services import InvitationValidator`

2. SERVICES (services/*.py):
   - CAN import models directly at module level (natural Django way)
   - CAN import other services
   - Example: `from ..models import Invitation, User`

3. SIGNALS (signals.py):
   - CAN import models and services at module level
   - Signals run after models are fully loaded, so no circular issues

4. VIEWS/SERIALIZERS/FORMS:
   - CAN import models and services at module level

The key principle: Services can depend on Models, but Models should NOT
depend on Services at module level. If a model needs a service, use lazy
imports inside methods.
This is a temporary solution and needs to be better organized
"""

from .invitation_validators import InvitationValidator
from .license_service import LicenseService, get_license_service
from .email_service import (
    send_invitation_email,
    send_invitation_accepted_email,
    send_invitation_revoked_email,
    resend_invitation_email,
)

__all__ = [
    "InvitationValidator",
    "LicenseService",
    "get_license_service",
    "send_invitation_email",
    "send_invitation_accepted_email",
    "send_invitation_revoked_email",
    "resend_invitation_email",
]
