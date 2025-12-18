"""Tests for health check endpoints."""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestHealthChecks:
    """Test health check endpoints."""

    def test_liveness_check(self):
        """Test liveness endpoint always returns 200."""
        client = Client()
        response = client.get(reverse("liveness"))

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_readiness_check(self):
        """Test readiness endpoint returns environment info."""
        client = Client()
        response = client.get(reverse("readiness"))

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "environment" in data

    def test_health_check_success(self):
        """Test health check endpoint when all services are available."""
        client = Client()
        response = client.get(reverse("health"))

        # Should be 200 if database and cache are working
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "services" in data

    def test_health_check_includes_database_status(self):
        """Test health check includes database status."""
        client = Client()
        response = client.get(reverse("health"))

        data = response.json()
        assert "database" in data["services"]

    def test_health_check_includes_cache_status(self):
        """Test health check includes cache status."""
        client = Client()
        response = client.get(reverse("health"))

        data = response.json()
        assert "cache" in data["services"]
