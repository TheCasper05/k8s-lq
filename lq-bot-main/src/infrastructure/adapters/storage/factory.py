"""Factory para crear adaptadores de storage."""

from src.config import Settings
from src.domain.ports.storage.file_storage_port import FileStoragePort
from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter


class StorageProviderFactory:
    """Factory para crear adaptadores de storage."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def create_storage_adapter(self, provider: str | None = None) -> FileStoragePort:
        """
        Crea un adaptador de storage según el proveedor especificado.

        Args:
            provider: Nombre del proveedor (boto3, local, etc.).
                     Si es None, usa el configurado en settings.storage_provider

        Returns:
            Adaptador de storage implementando FileStoragePort

        Raises:
            ValueError: Si el proveedor no está soportado
        """
        provider = provider or self.settings.storage_provider

        if provider == "boto3":
            return Boto3StorageAdapter(settings=self.settings)

        else:
            raise ValueError(
                f"Proveedor de storage '{provider}' no soportado. Proveedores disponibles: boto3"
            )
