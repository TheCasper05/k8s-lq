"""
Utilities for generating realtime JWT tokens with RSA/EC signing.

This module provides functionality to create short-lived JWT tokens specifically
for authenticating frontend connections to the lq-realtime-service.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from django.conf import settings


class RealtimeJWTError(Exception):
    """Base exception for realtime JWT operations."""

    pass


class MissingRealtimeConfigError(RealtimeJWTError):
    """Raised when required realtime JWT configuration is missing."""

    pass


def get_realtime_jwt_config() -> tuple[str, str, int]:
    """
    Get realtime JWT configuration from Django settings.

    Returns:
        tuple: (private_key, algorithm, expiration_minutes)

    Raises:
        MissingRealtimeConfigError: If required configuration is missing.
    """
    private_key = getattr(settings, "REALTIME_JWT_PRIVATE_KEY", None)
    algorithm = getattr(settings, "REALTIME_JWT_ALGORITHM", "RS256")
    expiration_minutes = getattr(settings, "REALTIME_JWT_EXPIRATION_MINUTES", 10)

    if not private_key:
        raise MissingRealtimeConfigError(
            "REALTIME_JWT_PRIVATE_KEY is not configured in settings. "
            "Please set this environment variable with your RSA/EC private key."
        )

    return private_key, algorithm, expiration_minutes


def generate_realtime_token(
    user_id: str,
    tenant_id: str,
    session_id: Optional[str] = None,
    expiration_minutes: Optional[int] = None,
) -> str:
    """
    Generate a short-lived JWT token for realtime service authentication.

    This token is specifically designed for frontend connections to lq-realtime-service.
    It is NOT a replacement for the main session JWT - it's a temporary access token
    with "realtime" scope.

    Args:
        user_id: The user's unique identifier (UUID string).
        tenant_id: The tenant/workspace identifier.
        session_id: Optional Django session ID for correlation.
        expiration_minutes: Optional custom expiration time (overrides config).

    Returns:
        str: Signed JWT token.

    Raises:
        MissingRealtimeConfigError: If JWT configuration is missing.
        jwt.PyJWTError: If token generation fails.

    Example:
        >>> token = generate_realtime_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     tenant_id="workspace-123",
        ...     session_id="abc123xyz"
        ... )
        >>> print(token)
        eyJ0eXAiOiJKV1QiLCJhbGc...
    """
    private_key, algorithm, default_expiration = get_realtime_jwt_config()

    # Use custom expiration or default from config
    exp_minutes = (
        expiration_minutes if expiration_minutes is not None else default_expiration
    )

    # Calculate expiration timestamp
    now = datetime.utcnow()
    expiration = now + timedelta(minutes=exp_minutes)

    # Build JWT payload
    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "tenant_id": str(tenant_id),
        "scope": "realtime",  # Scope identifier for realtime service
        "exp": int(expiration.timestamp()),  # Expiration time
        "iat": int(now.timestamp()),  # Issued at
        "jti": str(uuid.uuid4()),  # JWT ID for uniqueness/tracking
    }

    # Add session_id if provided
    if session_id:
        payload["session_id"] = session_id

    # Sign the token with RSA/EC private key
    try:
        token = jwt.encode(payload, private_key, algorithm=algorithm)
        return token
    except Exception as e:
        raise RealtimeJWTError(f"Failed to generate realtime JWT: {str(e)}") from e


def decode_realtime_token(token: str, verify: bool = True) -> dict:
    """
    Decode and optionally verify a realtime JWT token.

    Note: This function is primarily for debugging/testing in this service.
    The actual verification should happen in lq-realtime-service using the public key.

    Args:
        token: The JWT token to decode.
        verify: Whether to verify the signature (requires public key in settings).

    Returns:
        dict: Decoded payload.

    Raises:
        jwt.PyJWTError: If decoding/verification fails.
    """
    private_key, algorithm, _ = get_realtime_jwt_config()

    if verify:
        # For verification, we'd need the public key
        # This is mainly for testing purposes
        public_key = getattr(settings, "REALTIME_JWT_PUBLIC_KEY", None)
        if not public_key:
            raise MissingRealtimeConfigError(
                "REALTIME_JWT_PUBLIC_KEY is not configured. "
                "Cannot verify token without public key."
            )
        key = public_key
    else:
        # Decode without verification (for debugging)
        key = None

    options = {"verify_signature": verify}
    payload = jwt.decode(token, key, algorithms=[algorithm], options=options)

    return payload
