"""
Tests for authentication module.
"""

import pytest

from app.auth import (
    AuthenticationError,
    JWTManager,
    verify_webhook_signature,
)
from app.schemas import TokenPayload


class TestJWTManager:
    """Tests for JWTManager class."""

    def test_create_access_token(self):
        """Test creating an access token."""
        jwt_manager = JWTManager()

        token = jwt_manager.create_access_token(
            user_id="user123",
            tenant_id="tenant456",
            scope="ws:connect",
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        jwt_manager = JWTManager()

        # Create token
        token = jwt_manager.create_access_token(
            user_id="user123",
            tenant_id="tenant456",
            scope="ws:connect",
        )

        # Decode token
        payload = jwt_manager.decode_token(token)

        assert isinstance(payload, TokenPayload)
        assert payload.sub == "user123"
        assert payload.tenant_id == "tenant456"
        assert payload.scope == "ws:connect"

    def test_decode_expired_token(self):
        """Test decoding an expired token raises error."""
        import time

        import jwt

        from app.config import get_settings

        settings = get_settings()
        jwt_manager = JWTManager()

        # Create expired token (expired 1 minute ago, well beyond the 10s leeway)
        now = time.time()
        payload = {
            "sub": "user123",
            "tenant_id": "tenant456",
            "scope": "ws:connect",
            "iat": int(now - 600),  # Issued 10 minutes ago
            "exp": int(now - 60),  # Expired 1 minute ago
        }
        expired_token = jwt.encode(
            payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError, match="expired"):
            jwt_manager.decode_token(expired_token)

    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises error."""
        jwt_manager = JWTManager()

        with pytest.raises(AuthenticationError):
            jwt_manager.decode_token("invalid.token.here")

    def test_verify_scope_valid(self):
        """Test verifying valid scope."""
        jwt_manager = JWTManager()

        token = jwt_manager.create_access_token(
            user_id="user123",
            tenant_id="tenant456",
            scope="ws:connect",
        )

        payload = jwt_manager.decode_token(token)
        result = jwt_manager.verify_scope(payload, "ws:connect")

        assert result is True

    def test_verify_scope_invalid(self):
        """Test verifying invalid scope raises error."""
        jwt_manager = JWTManager()

        token = jwt_manager.create_access_token(
            user_id="user123",
            tenant_id="tenant456",
            scope="ws:connect",
        )

        payload = jwt_manager.decode_token(token)

        with pytest.raises(AuthenticationError, match="Insufficient scope"):
            jwt_manager.verify_scope(payload, "admin:write")


class TestWebhookSignature:
    """Tests for webhook signature verification."""

    @pytest.mark.asyncio
    async def test_verify_valid_signature(self):
        """Test verifying a valid webhook signature."""
        import hashlib
        import hmac

        payload = b'{"event": "test"}'
        secret = "test-secret"

        # Generate valid signature
        signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

        # Should not raise error
        result = await verify_webhook_signature(payload, signature, secret)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_invalid_signature(self):
        """Test verifying an invalid webhook signature raises error."""
        payload = b'{"event": "test"}'
        secret = "test-secret"
        invalid_signature = "invalid-signature-123"

        with pytest.raises(AuthenticationError, match="Invalid"):
            await verify_webhook_signature(payload, invalid_signature, secret)

    @pytest.mark.asyncio
    async def test_verify_signature_with_prefix(self):
        """Test verifying signature with sha256= prefix."""
        import hashlib
        import hmac

        payload = b'{"event": "test"}'
        secret = "test-secret"

        # Generate signature with prefix
        sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        signature = f"sha256={sig}"

        result = await verify_webhook_signature(payload, signature, secret)
        assert result is True
