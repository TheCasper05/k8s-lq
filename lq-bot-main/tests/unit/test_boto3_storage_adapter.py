"""Tests unitarios para Boto3StorageAdapter."""

from unittest.mock import MagicMock, patch

import pytest

from src.config import Settings
from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter


class TestBoto3StorageAdapter:
    """Tests para Boto3StorageAdapter."""

    @pytest.fixture
    def boto_settings(self):
        """Crea settings de prueba."""
        return Settings(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            aws_region_name="us-east-1",
            s3_endpoint_url="https://s3.test.com",
            s3_default_bucket="test-bucket",
            s3_max_attempts=3,
            s3_connect_timeout=5,
            s3_read_timeout=60,
        )

    @pytest.fixture
    def mock_boto_client(self):
        """Mock del cliente boto3."""
        return MagicMock()

    @pytest.fixture
    def storage_adapter(self, boto_settings, mock_boto_client):
        """Crea instancia de Boto3StorageAdapter con mock."""
        with patch("src.infrastructure.adapters.storage.boto3_storage_adapter.boto3"):
            adapter = Boto3StorageAdapter(boto_settings)
            adapter._client = mock_boto_client
            return adapter

    # ========== Tests de Inicialización ==========
    def test_init_with_settings(self, boto_settings):
        """Test: Boto3StorageAdapter se inicializa correctamente."""
        with patch("src.infrastructure.adapters.storage.boto3_storage_adapter.boto3"):
            adapter = Boto3StorageAdapter(boto_settings)
            assert adapter._settings == boto_settings

    # ========== Tests de Métodos Asíncronos ==========
    @pytest.mark.asyncio
    async def test_save_file_async(self, storage_adapter, mock_boto_client):
        """Test: save_file guarda archivo correctamente."""
        file_data = b"test content"
        file_name = "test.txt"
        folder = "uploads"

        result = await storage_adapter.save_file(file_data, file_name, folder)

        assert result == "uploads/test.txt"
        mock_boto_client.put_object.assert_called_once()
        call_args = mock_boto_client.put_object.call_args[1]
        assert call_args["Bucket"] == "test-bucket"
        assert call_args["Key"] == "uploads/test.txt"
        assert call_args["Body"] == file_data

    @pytest.mark.asyncio
    async def test_save_file_async_with_metadata(self, storage_adapter, mock_boto_client):
        """Test: save_file guarda metadata correctamente."""
        file_data = b"test content"
        file_name = "test.txt"
        metadata = {"user_id": "123", "type": "document"}

        await storage_adapter.save_file(file_data, file_name, metadata=metadata)

        call_args = mock_boto_client.put_object.call_args[1]
        assert "Metadata" in call_args
        assert call_args["Metadata"]["user_id"] == "123"
        assert call_args["Metadata"]["type"] == "document"

    @pytest.mark.asyncio
    async def test_get_file_async(self, storage_adapter, mock_boto_client):
        """Test: get_file obtiene archivo correctamente."""
        expected_content = b"file content"
        file_id = "uploads/test.txt"

        mock_body = MagicMock()
        mock_body.read.return_value = expected_content
        mock_boto_client.get_object.return_value = {"Body": mock_body}

        result = await storage_adapter.get_file(file_id)

        assert result == expected_content
        mock_boto_client.get_object.assert_called_once_with(Bucket="test-bucket", Key=file_id)

    @pytest.mark.asyncio
    async def test_delete_file_async_success(self, storage_adapter, mock_boto_client):
        """Test: delete_file elimina archivo exitosamente."""
        file_id = "uploads/test.txt"

        result = await storage_adapter.delete_file(file_id)

        assert result is True
        mock_boto_client.delete_object.assert_called_once_with(Bucket="test-bucket", Key=file_id)

    @pytest.mark.asyncio
    async def test_delete_file_async_failure(self, storage_adapter, mock_boto_client):
        """Test: delete_file retorna False en caso de error."""
        file_id = "uploads/test.txt"
        mock_boto_client.delete_object.side_effect = Exception("Error")

        result = await storage_adapter.delete_file(file_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_file_exists_async_true(self, storage_adapter, mock_boto_client):
        """Test: file_exists retorna True cuando el archivo existe."""
        file_id = "uploads/test.txt"
        mock_boto_client.head_object.return_value = {}

        result = await storage_adapter.file_exists(file_id)

        assert result is True
        mock_boto_client.head_object.assert_called_once_with(Bucket="test-bucket", Key=file_id)

    @pytest.mark.asyncio
    async def test_file_exists_async_false(self, storage_adapter, mock_boto_client):
        """Test: file_exists retorna False cuando el archivo no existe."""
        file_id = "uploads/test.txt"
        mock_boto_client.head_object.side_effect = Exception("Not found")

        result = await storage_adapter.file_exists(file_id)

        assert result is False

    # ========== Tests de Métodos Síncronos ==========
    def test_save_file_sync(self, storage_adapter, mock_boto_client):
        """Test: save_file_sync guarda archivo correctamente."""
        file_data = b"test content"
        file_name = "test.txt"
        folder = "uploads"

        result = storage_adapter.save_file_sync(file_data, file_name, folder)

        assert result == "uploads/test.txt"
        mock_boto_client.put_object.assert_called_once()

    def test_get_file_sync(self, storage_adapter, mock_boto_client):
        """Test: get_file_sync obtiene archivo correctamente."""
        expected_content = b"file content"
        file_id = "uploads/test.txt"

        mock_body = MagicMock()
        mock_body.read.return_value = expected_content
        mock_boto_client.get_object.return_value = {"Body": mock_body}

        result = storage_adapter.get_file_sync(file_id)

        assert result == expected_content

    def test_delete_file_sync_success(self, storage_adapter, mock_boto_client):
        """Test: delete_file_sync elimina archivo exitosamente."""
        file_id = "uploads/test.txt"

        result = storage_adapter.delete_file_sync(file_id)

        assert result is True

    def test_delete_file_sync_failure(self, storage_adapter, mock_boto_client):
        """Test: delete_file_sync retorna False en caso de error."""
        file_id = "uploads/test.txt"
        mock_boto_client.delete_object.side_effect = Exception("Error")

        result = storage_adapter.delete_file_sync(file_id)

        assert result is False

    def test_file_exists_sync_true(self, storage_adapter, mock_boto_client):
        """Test: file_exists_sync retorna True cuando el archivo existe."""
        file_id = "uploads/test.txt"
        mock_boto_client.head_object.return_value = {}

        result = storage_adapter.file_exists_sync(file_id)

        assert result is True

    def test_file_exists_sync_false(self, storage_adapter, mock_boto_client):
        """Test: file_exists_sync retorna False cuando el archivo no existe."""
        file_id = "uploads/test.txt"
        mock_boto_client.head_object.side_effect = Exception("Not found")

        result = storage_adapter.file_exists_sync(file_id)

        assert result is False

    # ========== Tests de Métodos Adicionales ==========
    def test_download_to_path(self, storage_adapter, mock_boto_client, tmp_path):
        """Test: download_to_path descarga archivo correctamente."""
        file_id = "uploads/test.txt"
        destination = tmp_path / "downloaded.txt"
        test_content = b"file content"

        mock_body = MagicMock()
        mock_body.read.side_effect = [test_content, b""]
        mock_boto_client.get_object.return_value = {"Body": mock_body}

        result = storage_adapter._download_to_path(file_id, destination)

        assert result == destination
        assert destination.exists()
        assert destination.read_bytes() == test_content

    def test_download_to_path_creates_directories(
        self, storage_adapter, mock_boto_client, tmp_path
    ):
        """Test: download_to_path crea directorios si no existen."""
        file_id = "test.txt"
        destination = tmp_path / "new" / "dir" / "file.txt"

        mock_body = MagicMock()
        mock_body.read.side_effect = [b"content", b""]
        mock_boto_client.get_object.return_value = {"Body": mock_body}

        result = storage_adapter._download_to_path(file_id, destination)

        assert result.parent.exists()
        assert result.exists()

    def test_download_to_path_with_custom_bucket(self, storage_adapter, mock_boto_client, tmp_path):
        """Test: download_to_path usa bucket personalizado."""
        file_id = "test.txt"
        destination = tmp_path / "file.txt"
        custom_bucket = "custom-bucket"

        mock_body = MagicMock()
        mock_body.read.side_effect = [b"content", b""]
        mock_boto_client.get_object.return_value = {"Body": mock_body}

        storage_adapter._download_to_path(file_id, destination, bucket=custom_bucket)

        mock_boto_client.get_object.assert_called_once_with(Bucket=custom_bucket, Key=file_id)

    def test_generate_presigned_url(self, storage_adapter, mock_boto_client):
        """Test: generate_presigned_url genera URL correctamente."""
        file_id = "uploads/test.txt"
        expected_url = "https://s3.test.com/test-bucket/uploads/test.txt?signature=abc"
        expires_in = 3600

        mock_boto_client.generate_presigned_url.return_value = expected_url

        result = storage_adapter._generate_presigned_url(file_id, expires_in=expires_in)

        assert result == expected_url
        mock_boto_client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": "test-bucket", "Key": file_id},
            ExpiresIn=expires_in,
        )

    def test_generate_presigned_url_default_expires(self, storage_adapter, mock_boto_client):
        """Test: generate_presigned_url usa expires_in por defecto."""
        file_id = "test.txt"
        mock_boto_client.generate_presigned_url.return_value = "https://url.com"

        storage_adapter._generate_presigned_url(file_id)

        call_args = mock_boto_client.generate_presigned_url.call_args[1]
        assert call_args["ExpiresIn"] == 3600

    def test_generate_presigned_url_with_custom_bucket(self, storage_adapter, mock_boto_client):
        """Test: generate_presigned_url usa bucket personalizado."""
        file_id = "test.txt"
        custom_bucket = "custom-bucket"
        mock_boto_client.generate_presigned_url.return_value = "https://url.com"

        storage_adapter._generate_presigned_url(file_id, bucket=custom_bucket)

        call_args = mock_boto_client.generate_presigned_url.call_args[1]
        assert call_args["Params"]["Bucket"] == custom_bucket

    # ========== Tests de Helpers Internos ==========
    def test_get_bucket_with_default(self, storage_adapter):
        """Test: _get_bucket retorna bucket por defecto."""
        result = storage_adapter._get_bucket()
        assert result == "test-bucket"

    def test_get_bucket_with_explicit(self, storage_adapter):
        """Test: _get_bucket retorna bucket explícito."""
        result = storage_adapter._get_bucket("custom-bucket")
        assert result == "custom-bucket"

    def test_get_bucket_raises_error_when_no_bucket(self, mock_boto_client):
        """Test: _get_bucket lanza error cuando no hay bucket."""
        boto_settings = Settings(
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            aws_region_name="us-east-1",
            s3_default_bucket=None,  # Sin bucket
        )
        with patch("src.infrastructure.adapters.storage.boto3_storage_adapter.boto3"):
            adapter = Boto3StorageAdapter(boto_settings)
            adapter._client = mock_boto_client

            with pytest.raises(ValueError, match="Bucket no especificado"):
                adapter._get_bucket()

    def test_build_key_without_folder(self, storage_adapter):
        """Test: _build_key sin folder."""
        result = storage_adapter._build_key("test.txt")
        assert result == "test.txt"

    def test_build_key_with_folder(self, storage_adapter):
        """Test: _build_key con folder."""
        result = storage_adapter._build_key("test.txt", "uploads")
        assert result == "uploads/test.txt"

    def test_build_key_with_folder_strips_slashes(self, storage_adapter):
        """Test: _build_key normaliza slashes en folder."""
        result = storage_adapter._build_key("test.txt", "/uploads/")
        assert result == "uploads/test.txt"

    def test_build_key_with_empty_folder(self, storage_adapter):
        """Test: _build_key con folder vacío."""
        result = storage_adapter._build_key("test.txt", "")
        assert result == "test.txt"
