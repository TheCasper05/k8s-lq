"""
Utility helpers shared across JWT authentication views.
"""

from allauth.account import app_settings as allauth_app_settings
from allauth.account.models import EmailAddress
from allauth.core.internal import ratelimit as allauth_ratelimit
from django.contrib.auth import get_user_model

User = get_user_model()


def _client_ip(request) -> str:
    """
    Extract client IP from request headers.
    """
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _is_email_verified(user):
    """
    Check whether the user's primary email is verified in allauth.
    """
    email_record = EmailAddress.objects.filter(
        user=user, email__iexact=user.email
    ).first()
    return bool(email_record and email_record.verified)


def _ratelimit(request, action: str, key: str):
    """
    Apply allauth rate limits for the given action/key.
    """
    limits = getattr(allauth_app_settings, "RATE_LIMITS", None)
    if not limits:
        return True
    ip = _client_ip(request)
    composite_key = key.lower()
    if ip:
        composite_key = f"{composite_key}:{ip}"
    return allauth_ratelimit.consume(
        request,
        config=limits,
        action=action,
        key=composite_key,
        raise_exception=False,
        limit_get=True,
    )


__all__ = ["_client_ip", "_is_email_verified", "_ratelimit"]
