import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture para cliente API."""
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Fixture para usuario autenticado."""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    """Fixture para cliente API autenticado."""
    api_client.force_login(authenticated_user)
    return api_client


class TestPresignedURLView:
    """Tests para la view de generación de URLs prefirmadas."""

    def test_unauthenticated_request(self, api_client):
        """Test que request no autenticado retorna 401 (JWT authentication)."""
        response = api_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch("boto3.client")
    def test_valid_request_returns_presigned_url(
        self, mock_boto_client, authenticated_client
    ):
        """Test que request válido retorna URL prefirmada."""
        # Mock del cliente boto3
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = (
            "https://example.com/presigned-url"
        )
        mock_boto_client.return_value = mock_s3

        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "upload_url" in response.data
        assert "headers" in response.data
        assert "file_path" in response.data
        assert response.data["upload_url"] == "https://example.com/presigned-url"

    def test_invalid_category(self, authenticated_client):
        """Test que categoría inválida retorna error de validación."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "invalid",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "file_category" in response.data

    def test_file_size_exceeds_limit(self, authenticated_client):
        """Test que tamaño excedido retorna error de validación."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 150 * 1024 * 1024,  # 150MB > 100MB global limit
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_extension_for_category(self, authenticated_client):
        """Test que extensión inválida para categoría retorna error."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "image",  # .mp3 no es válido para image
                "usage": "conversation/uuid/image/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_usage_inconsistency(self, authenticated_client):
        """Test que usage inconsistente retorna error."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/other.mp3",  # Nombre diferente
                "file_size": 5242880,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_usage_missing_category(self, authenticated_client):
        """Test que usage sin categoría retorna error."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/test.mp3",  # Sin 'audio' en el path
                "file_size": 5242880,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("boto3.client")
    def test_boto3_client_error(self, mock_boto_client, authenticated_client):
        """Test manejo de error de boto3."""
        from botocore.exceptions import ClientError

        # Mock del cliente boto3 que lanza error
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "generate_presigned_url",
        )
        mock_boto_client.return_value = mock_s3

        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data

    @patch("boto3.client")
    def test_unexpected_error(self, mock_boto_client, authenticated_client):
        """Test manejo de error inesperado."""
        # Mock del cliente boto3 que lanza error genérico
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = Exception("Unexpected error")
        mock_boto_client.return_value = mock_s3

        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                "file_category": "audio",
                "usage": "conversation/uuid/audio/test.mp3",
                "file_size": 5242880,
            },
            format="json",
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data

    def test_missing_required_fields(self, authenticated_client):
        """Test que campos requeridos faltantes retornan error."""
        response = authenticated_client.post(
            "/files/presigned-url/",
            {
                "file_name": "test.mp3",
                # Faltan otros campos
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
