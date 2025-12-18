"""
Pytest configuration and fixtures.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing anything
os.environ["REDIS_HOST"] = "localhost"
os.environ["TESTING"] = "true"

from app.auth import jwt_manager
from app.config import get_settings

settings = get_settings()


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis client for all tests automatically."""
    with patch("app.redis_client.redis_client") as mock:
        # Mock all connection methods
        mock.connect = AsyncMock()
        mock.disconnect = AsyncMock()
        mock.is_connected = AsyncMock(return_value=True)
        mock.ping = AsyncMock(return_value=True)
        mock.publish = AsyncMock(return_value=0)
        mock.subscribe = AsyncMock()
        mock.unsubscribe = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock()
        mock.delete = AsyncMock()
        mock.redis = AsyncMock()
        mock.redis.ping = AsyncMock(return_value=True)

        # Patch in all modules that import redis_client
        with (
            patch("app.main.redis_client", mock),
            patch("app.websocket_handler.redis_client", mock),
        ):
            yield mock


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def valid_token():
    """Generate a valid JWT token for testing."""
    token = jwt_manager.create_access_token(
        user_id="test-user-123",
        tenant_id="test-tenant-456",
        scope="ws:connect",
        additional_claims={"user_role": "admin"},
    )
    return token


@pytest.fixture
def expired_token():
    """Generate an expired JWT token for testing."""
    from datetime import datetime, timedelta

    import jwt

    payload = {
        "sub": "test-user-123",
        "tenant_id": "test-tenant-456",
        "scope": "ws:connect",
        "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture
def webhook_payload():
    """Sample webhook payload."""
    return {
        "event_type": "test.event",
        "tenant_id": "test-tenant-456",
        "data": {"message": "Test webhook event"},
    }
