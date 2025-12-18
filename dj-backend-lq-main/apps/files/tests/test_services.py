import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings
from botocore.exceptions import ClientError
from ..services import PresignedURLService


class TestPresignedURLService:
    """Tests para el servicio de generación de URLs prefirmadas."""

    @override_settings(
        AWS_ACCESS_KEY_ID="test-key",
        AWS_SECRET_ACCESS_KEY="test-secret",
        AWS_STORAGE_BUCKET_NAME="test-bucket",
        AWS_S3_ENDPOINT_URL="https://lq-storage-qa.nyc3.digitaloceanspaces.com",
        AWS_LOCATION="media",
        AWS_DEFAULT_ACL="public-read",
        DO_SPACES_PRESIGN_EXPIRE_SECONDS=3600,
    )
    @patch("apps.files.services.boto3.client")
    def test_generate_presigned_url_success(self, mock_boto_client):
        """Test generación exitosa de URL prefirmada."""
        # Mock del cliente S3
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.return_value = (
            "https://example.com/presigned-url"
        )
        mock_boto_client.return_value = mock_s3_client

        service = PresignedURLService()
        result = service.generate_presigned_url(
            file_path="media/conversation/uuid/audio/file.mp3",
            file_size=5242880,  # 5MB
        )

        assert "upload_url" in result
        assert "headers" in result
        assert "file_path" in result
        assert result["upload_url"] == "https://example.com/presigned-url"
        assert result["headers"]["Content-Length"] == "5242880"
        assert result["headers"]["x-amz-acl"] == "public-read"
        assert result["file_path"] == "media/conversation/uuid/audio/file.mp3"

        # Verificar que se llamó con los parámetros correctos
        mock_s3_client.generate_presigned_url.assert_called_once()
        call_kwargs = mock_s3_client.generate_presigned_url.call_args
        assert call_kwargs[1]["Params"]["Bucket"] == "test-bucket"
        assert (
            call_kwargs[1]["Params"]["Key"] == "media/conversation/uuid/audio/file.mp3"
        )
        assert call_kwargs[1]["Params"]["ContentLength"] == 5242880
        assert call_kwargs[1]["Params"]["ACL"] == "public-read"
        assert call_kwargs[1]["ExpiresIn"] == 3600

    @override_settings(
        AWS_ACCESS_KEY_ID="test-key",
        AWS_SECRET_ACCESS_KEY="test-secret",
        AWS_STORAGE_BUCKET_NAME="test-bucket",
        AWS_S3_ENDPOINT_URL="https://lq-storage-qa.nyc3.digitaloceanspaces.com",
        AWS_LOCATION="media",
        AWS_DEFAULT_ACL="public-read",
        DO_SPACES_PRESIGN_EXPIRE_SECONDS=3600,
    )
    @patch("apps.files.services.boto3.client")
    def test_generate_presigned_url_with_custom_expiration(self, mock_boto_client):
        """Test generación de URL con expiración personalizada."""
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.return_value = (
            "https://example.com/presigned-url"
        )
        mock_boto_client.return_value = mock_s3_client

        service = PresignedURLService()
        service.generate_presigned_url(
            file_path="media/conversation/uuid/audio/file.mp3",
            file_size=5242880,
            expiration=7200,  # 2 horas
        )

        call_kwargs = mock_s3_client.generate_presigned_url.call_args
        assert call_kwargs[1]["ExpiresIn"] == 7200

    @override_settings(
        AWS_ACCESS_KEY_ID="test-key",
        AWS_SECRET_ACCESS_KEY="test-secret",
        AWS_STORAGE_BUCKET_NAME="test-bucket",
        AWS_S3_ENDPOINT_URL="https://lq-storage-qa.nyc3.digitaloceanspaces.com",
        AWS_LOCATION="media",
    )
    @patch("apps.files.services.boto3.client")
    def test_generate_presigned_url_client_error(self, mock_boto_client):
        """Test manejo de error de cliente S3."""
        mock_s3_client = MagicMock()
        mock_s3_client.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "generate_presigned_url",
        )
        mock_boto_client.return_value = mock_s3_client

        service = PresignedURLService()
        with pytest.raises(ClientError):
            service.generate_presigned_url(
                file_path="media/conversation/uuid/audio/file.mp3",
                file_size=5242880,
            )

    @override_settings(
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
        AWS_STORAGE_BUCKET_NAME="",
    )
    def test_service_initialization_missing_config(self):
        """Test que falta de configuración lanza ImproperlyConfigured."""
        from django.core.exceptions import ImproperlyConfigured

        with pytest.raises(ImproperlyConfigured):
            PresignedURLService()

    def test_build_file_path(self):
        """Test construcción de path completo."""
        with override_settings(
            AWS_ACCESS_KEY_ID="test-key",
            AWS_SECRET_ACCESS_KEY="test-secret",
            AWS_STORAGE_BUCKET_NAME="test-bucket",
            AWS_S3_ENDPOINT_URL="https://lq-storage-qa.nyc3.digitaloceanspaces.com",
            AWS_LOCATION="media",
        ):
            with patch("apps.files.services.boto3.client"):
                service = PresignedURLService()

                # Test path normal
                result = service.build_file_path("conversation/uuid/audio/file.mp3")
                assert result == "media/conversation/uuid/audio/file.mp3"

                # Test path que ya tiene / al inicio
                result = service.build_file_path("/conversation/uuid/audio/file.mp3")
                assert result == "media/conversation/uuid/audio/file.mp3"

                # Test location sin /
                with override_settings(AWS_LOCATION="media"):
                    service = PresignedURLService()
                    result = service.build_file_path("conversation/uuid/audio/file.mp3")
                    assert result == "media/conversation/uuid/audio/file.mp3"
