"""
Tests for API endpoints.
"""

from fastapi import status


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "active_connections" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


class TestMetrics:
    """Tests for metrics endpoint."""

    def test_metrics(self, client):
        """Test metrics endpoint returns metrics data."""
        response = client.get("/metrics")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "active_websocket_connections" in data
        assert "total_messages_sent" in data
        assert "uptime_seconds" in data
        assert "memory_usage_mb" in data


class TestWebhooks:
    """Tests for webhook endpoints."""

    def test_webhook_stripe(self, client, webhook_payload):
        """Test Stripe webhook endpoint."""
        response = client.post(
            "/webhooks/stripe",
            json=webhook_payload,
            headers={"x-tenant-id": "test-tenant-456"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "accepted"
        assert data["provider"] == "stripe"

    def test_webhook_github(self, client, webhook_payload):
        """Test GitHub webhook endpoint."""
        response = client.post(
            "/webhooks/github",
            json=webhook_payload,
            headers={"x-tenant-id": "test-tenant-456"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["provider"] == "github"

    def test_webhook_custom(self, client, webhook_payload):
        """Test custom webhook endpoint."""
        response = client.post(
            "/webhooks/custom",
            json=webhook_payload,
            headers={"x-tenant-id": "test-tenant-456"},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_webhook_invalid_json(self, client):
        """Test webhook with invalid JSON returns 400."""
        response = client.post(
            "/webhooks/custom",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
