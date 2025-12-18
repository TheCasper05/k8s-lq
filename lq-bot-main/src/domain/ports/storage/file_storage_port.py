from abc import ABC, abstractmethod
from typing import Any


class FileStoragePort(ABC):
    """Port para gestión de archivos (local, S3, etc.)."""

    @abstractmethod
    async def save_file(
        self,
        file_data: bytes,
        file_name: str,
        folder: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Guarda un archivo y retorna su identificador/ruta.

        Args:
            file_data: Datos binarios del archivo
            file_name: Nombre del archivo
            folder: Carpeta destino (opcional)
            metadata: Metadata adicional del archivo

        Returns:
            Identificador o ruta del archivo guardado
        """
        pass

    @abstractmethod
    async def get_file(self, file_id: str) -> bytes:
        """
        Obtiene los datos de un archivo por su ID/ruta.

        Args:
            file_id: Identificador del archivo

        Returns:
            Datos binarios del archivo
        """
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """
        Elimina un archivo.

        Args:
            file_id: Identificador del archivo

        Returns:
            True si se eliminó correctamente
        """
        pass

    @abstractmethod
    async def file_exists(self, file_id: str) -> bool:
        """
        Verifica si un archivo existe.

        Args:
            file_id: Identificador del archivo

        Returns:
            True si el archivo existe
        """
        pass

    @abstractmethod
    def save_file_sync(
        self,
        file_data: bytes,
        file_name: str,
        folder: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Versión síncrona de save_file."""
        pass

    @abstractmethod
    def get_file_sync(self, file_id: str) -> bytes:
        """Versión síncrona de get_file."""
        pass

    @abstractmethod
    def delete_file_sync(self, file_id: str) -> bool:
        """Versión síncrona de delete_file."""
        pass

    @abstractmethod
    def file_exists_sync(self, file_id: str) -> bool:
        """Versión síncrona de file_exists."""
        pass
