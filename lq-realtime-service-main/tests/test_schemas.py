"""
Tests for Pydantic schemas.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import (
    TokenPayload,
    WebhookEvent,
    WebhookProvider,
    WSMessage,
    WSMessageType,
)


class TestTokenPayload:
    """Tests for TokenPayload schema."""

    def test_valid_token_payload(self):
        """Test creating a valid token payload."""
        payload = TokenPayload(
            sub="user123",
            tenant_id="tenant456",
            scope="ws:connect",
            exp=1234567890,
        )

        assert payload.sub == "user123"
        assert payload.tenant_id == "tenant456"
        assert payload.scope == "ws:connect"
        assert payload.exp == 1234567890

    def test_token_payload_with_metadata(self):
        """Test token payload with additional metadata."""
        payload = TokenPayload(
            sub="user123",
            tenant_id="tenant456",
            scope="ws:connect",
            exp=1234567890,
            metadata={"role": "admin", "permissions": ["read", "write"]},
        )

        assert payload.metadata == {"role": "admin", "permissions": ["read", "write"]}

    def test_token_payload_missing_required(self):
        """Test token payload with missing required fields raises error."""
        with pytest.raises(ValidationError):
            TokenPayload(tenant_id="tenant456", scope="ws:connect")


class TestWSMessage:
    """Tests for WSMessage schema."""

    def test_valid_ws_message(self):
        """Test creating a valid WebSocket message."""
        message = WSMessage(
            type=WSMessageType.MESSAGE,
            payload={"text": "Hello, world!"},
        )

        assert message.type == WSMessageType.MESSAGE
        assert message.payload == {"text": "Hello, world!"}
        assert isinstance(message.timestamp, datetime)

    def test_ws_message_ping(self):
        """Test creating a ping message."""
        message = WSMessage(type=WSMessageType.PING)

        assert message.type == WSMessageType.PING
        assert message.payload == {}

    def test_ws_message_with_user_info(self):
        """Test WebSocket message with user information."""
        message = WSMessage(
            type=WSMessageType.MESSAGE,
            payload={"text": "Hello"},
            from_user="user123",
            to_user="user456",
        )

        assert message.from_user == "user123"
        assert message.to_user == "user456"


class TestWebhookEvent:
    """Tests for WebhookEvent schema."""

    def test_valid_webhook_event(self):
        """Test creating a valid webhook event."""
        event = WebhookEvent(
            provider=WebhookProvider.STRIPE,
            event_type="charge.succeeded",
            payload={"amount": 1000, "currency": "usd"},
        )

        assert event.provider == WebhookProvider.STRIPE
        assert event.event_type == "charge.succeeded"
        assert event.payload["amount"] == 1000

    def test_webhook_event_with_tenant(self):
        """Test webhook event with tenant ID."""
        event = WebhookEvent(
            provider=WebhookProvider.GITHUB,
            event_type="push",
            payload={"ref": "refs/heads/main"},
            tenant_id="tenant123",
        )

        assert event.tenant_id == "tenant123"

    def test_webhook_event_serialization(self):
        """Test webhook event can be serialized to dict."""
        event = WebhookEvent(
            provider=WebhookProvider.CUSTOM,
            event_type="test.event",
            payload={"data": "test"},
        )

        data = event.model_dump()
        assert data["provider"] == "custom"
        assert "received_at" in data
