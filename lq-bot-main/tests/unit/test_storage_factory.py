"""Tests unitarios para StorageProviderFactory."""

from unittest.mock import MagicMock, patch

import pytest

from src.config import Settings
from src.infrastructure.adapters.storage.factory import StorageProviderFactory


@pytest.fixture
def mock_settings():
    """Crea un mock de Settings."""
    settings = MagicMock(spec=Settings)
    settings.storage_provider = "boto3"
    return settings


@pytest.fixture
def factory(mock_settings):
    """Crea una instancia del factory con settings mockeados."""
    return StorageProviderFactory(settings=mock_settings)


class TestStorageProviderFactory:
    """Tests para StorageProviderFactory."""

    def test_init_with_settings(self, mock_settings):
        """Test: StorageProviderFactory se inicializa correctamente."""
        factory = StorageProviderFactory(settings=mock_settings)
        assert factory.settings == mock_settings

    @patch("src.infrastructure.adapters.storage.factory.Boto3StorageAdapter")
    def test_create_storage_adapter_with_boto3_provider(self, mock_boto3_adapter, factory):
        """Test: crear adaptador boto3 cuando se especifica 'boto3'."""
        # Arrange
        mock_adapter_instance = MagicMock()
        mock_boto3_adapter.return_value = mock_adapter_instance

        # Act
        result = factory.create_storage_adapter(provider="boto3")

        # Assert
        assert result == mock_adapter_instance
        mock_boto3_adapter.assert_called_once_with(settings=factory.settings)

    @patch("src.infrastructure.adapters.storage.factory.Boto3StorageAdapter")
    def test_create_storage_adapter_with_none_provider_uses_settings(
        self, mock_boto3_adapter, factory
    ):
        """Test: crear adaptador usando provider de settings cuando provider es None."""
        # Arrange
        factory.settings.storage_provider = "boto3"
        mock_adapter_instance = MagicMock()
        mock_boto3_adapter.return_value = mock_adapter_instance

        # Act
        result = factory.create_storage_adapter(provider=None)

        # Assert
        assert result == mock_adapter_instance
        mock_boto3_adapter.assert_called_once_with(settings=factory.settings)

    @patch("src.infrastructure.adapters.storage.factory.Boto3StorageAdapter")
    def test_create_storage_adapter_with_default_settings(self, mock_boto3_adapter, factory):
        """Test: crear adaptador sin especificar provider usa settings por defecto."""
        # Arrange
        factory.settings.storage_provider = "boto3"
        mock_adapter_instance = MagicMock()
        mock_boto3_adapter.return_value = mock_adapter_instance

        # Act
        result = factory.create_storage_adapter()

        # Assert
        assert result == mock_adapter_instance
        mock_boto3_adapter.assert_called_once_with(settings=factory.settings)

    def test_create_storage_adapter_raises_error_for_unsupported_provider(self, factory):
        """Test: lanzar error cuando el proveedor no está soportado."""
        # Arrange
        unsupported_provider = "unsupported_provider"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            factory.create_storage_adapter(provider=unsupported_provider)

        assert f"Proveedor de storage '{unsupported_provider}' no soportado" in str(exc_info.value)
        assert "boto3" in str(exc_info.value)

    def test_create_storage_adapter_raises_error_when_settings_provider_unsupported(self):
        """Test: lanzar error cuando el provider en settings no está soportado."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.storage_provider = "invalid_provider"
        factory = StorageProviderFactory(settings=settings)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            factory.create_storage_adapter()

        assert "Proveedor de storage 'invalid_provider' no soportado" in str(exc_info.value)
