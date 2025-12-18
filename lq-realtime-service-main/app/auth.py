"""
JWT Authentication module.
Handles token validation, decoding, and scope verification.
"""

import logging
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas import TokenPayload

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    pass


class JWTManager:
    """JWT token manager for encoding and decoding tokens."""

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.expire_minutes = settings.jwt_access_token_expire_minutes

    def create_access_token(
        self,
        user_id: str,
        tenant_id: str,
        scope: str = "ws:connect",
        additional_claims: dict | None = None,
    ) -> str:
        """
        Create a new JWT access token.

        Args:
            user_id: User identifier
            tenant_id: Tenant/organization identifier
            scope: Token scope (default: ws:connect)
            additional_claims: Additional JWT claims

        Returns:
            Encoded JWT token string
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.expire_minutes)

        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "scope": scope,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
        }

        if additional_claims:
            payload.update(additional_claims)

        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenPayload with decoded claims

        Raises:
            AuthenticationError: If token is invalid, expired, or malformed
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": True,
                    "verify_iat": False,  # Disable iat verification to avoid clock skew issues
                },
                leeway=10,  # 10 seconds leeway for clock skew
            )

            # Validate required fields
            if not payload.get("sub"):
                raise AuthenticationError("Token missing 'sub' (user ID)")

            if not payload.get("tenant_id"):
                raise AuthenticationError("Token missing 'tenant_id'")

            if not payload.get("exp"):
                raise AuthenticationError("Token missing 'exp' (expiration)")

            return TokenPayload(**payload)

        except jwt.ExpiredSignatureError as e:
            logger.warning("Token has expired")
            raise AuthenticationError("Token has expired") from e

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e!s}")
            raise AuthenticationError(f"Invalid token: {e!s}") from e

        except Exception as e:
            logger.error(f"Token decode error: {e!s}")
            raise AuthenticationError(f"Token decode error: {e!s}") from e

    def verify_scope(self, token_payload: TokenPayload, required_scope: str) -> bool:
        """
        Verify token has required scope.

        Args:
            token_payload: Decoded token payload
            required_scope: Required scope string

        Returns:
            True if token has required scope

        Raises:
            AuthenticationError: If scope is missing or invalid
        """
        token_scope = token_payload.scope

        # Support both single scope and space-separated scopes
        if isinstance(token_scope, str):
            scopes = token_scope.split()
        else:
            scopes = [token_scope]

        if required_scope not in scopes:
            raise AuthenticationError(
                f"Insufficient scope. Required: {required_scope}, Got: {token_scope}"
            )

        return True


# Global JWT manager instance
jwt_manager = JWTManager()


async def verify_websocket_token(token: str) -> TokenPayload:
    """
    Verify WebSocket connection token.

    Args:
        token: JWT token from query parameters

    Returns:
        TokenPayload with validated claims

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode token
        payload = jwt_manager.decode_token(token)

        # Verify WebSocket scope
        jwt_manager.verify_scope(payload, "ws:connect")

        logger.info(f"WebSocket token verified for user={payload.sub}, tenant={payload.tenant_id}")

        return payload

    except AuthenticationError as e:
        logger.warning(f"WebSocket authentication failed: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


async def verify_webhook_signature(
    payload: bytes, signature: str, secret: str, algorithm: str = "sha256"
) -> bool:
    """
    Verify webhook HMAC signature.

    Args:
        payload: Raw webhook payload bytes
        signature: Signature from webhook header
        secret: Webhook signing secret
        algorithm: Hash algorithm (default: sha256)

    Returns:
        True if signature is valid

    Raises:
        AuthenticationError: If signature is invalid
    """
    import hashlib
    import hmac

    try:
        # Remove common signature prefixes (e.g., "sha256=")
        if "=" in signature:
            _, sig_value = signature.split("=", 1)
        else:
            sig_value = signature

        # Compute expected signature
        expected_signature = hmac.new(
            secret.encode(), payload, getattr(hashlib, algorithm)
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, sig_value)

        if not is_valid:
            raise AuthenticationError("Invalid webhook signature")

        logger.info("Webhook signature verified successfully")
        return True

    except Exception as e:
        logger.error(f"Webhook signature verification failed: {e!s}")
        raise AuthenticationError(f"Signature verification failed: {e!s}") from e


async def verify_system_api_key(api_key: str) -> bool:
    """
    Verify system API key for privileged operations.
    This is used for admin-level operations like global broadcasts.

    Args:
        api_key: API key from header

    Returns:
        True if API key is valid

    Raises:
        HTTPException: If API key is invalid or missing
    """
    import hmac

    if not api_key:
        logger.warning("System API key missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="System API key required",
        )

    # Constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(api_key, settings.system_api_key)

    if not is_valid:
        logger.warning("Invalid system API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid system API key",
        )

    logger.info("System API key verified successfully")
    return True
