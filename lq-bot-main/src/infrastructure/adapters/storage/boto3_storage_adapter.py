"""Adapter de storage usando boto3 (S3-compatible)."""

import asyncio
from io import BufferedReader
from pathlib import Path
from typing import Any

import boto3
from botocore.client import Config

from src.config import Settings
from src.domain.ports.storage.file_storage_port import FileStoragePort


class Boto3StorageAdapter(FileStoragePort):
    """
    Adapter de storage usando boto3 para AWS S3 o DigitalOcean Spaces.

    Implementa FileStoragePort siguiendo arquitectura hexagonal.
    """

    def __init__(self, settings: Settings):
        """
        Inicializa el adapter de storage con boto3.

        Args:
            settings: Configuración de boto3/S3
        """
        self._settings = settings
        self._client_cache = None  # Lazy initialization

    @property
    def _client(self):
        """Obtiene el cliente boto3, creándolo si no existe (lazy initialization)."""
        if self._client_cache is None:
            self._client_cache = self._build_boto3_client()
        return self._client_cache

    @_client.setter
    def _client(self, value):
        """Setter para permitir mockear el cliente en tests."""
        self._client_cache = value

    def _build_boto3_client(self):
        """Construye el cliente boto3 S3."""
        cfg = Config(
            s3={"addressing_style": "virtual"},
            retries={"max_attempts": self._settings.s3_max_attempts, "mode": "standard"},
            connect_timeout=self._settings.s3_connect_timeout,
            read_timeout=self._settings.s3_read_timeout,
            signature_version="s3v4",
        )

        # Asegurar que las credenciales no sean None o vacías
        access_key = self._settings.aws_access_key_id or ""
        secret_key = self._settings.aws_secret_access_key or ""

        session = boto3.session.Session(
            aws_access_key_id=access_key if access_key else None,
            aws_secret_access_key=secret_key if secret_key else None,
            region_name=self._settings.aws_region_name,
        )
        return session.client("s3", endpoint_url=self._settings.s3_endpoint_url, config=cfg)

    def _get_bucket(self, bucket: str | None = None) -> str:
        """Retorna el bucket a usar, validando que exista."""
        b = bucket or self._settings.s3_default_bucket
        if not b:
            raise ValueError(
                "Bucket no especificado. Configura s3_default_bucket o pasa bucket explícito."
            )
        return b

    def _build_key(self, file_name: str, folder: str | None = None) -> str:
        """Construye la key de S3 a partir del nombre del archivo y la carpeta."""
        if folder:
            folder = folder.strip("/")
            return f"{folder}/{file_name}" if folder else file_name
        return file_name

    def _download_to_path(
        self, file_id: str, destination: str | Path, bucket: str | None = None
    ) -> Path:
        """
        Descarga un archivo a una ruta local.

        Args:
            file_id: Key del archivo en S3
            destination: Ruta de destino local
            bucket: Bucket personalizado (opcional)

        Returns:
            Path al archivo descargado
        """
        bucket = self._get_bucket(bucket)
        dst_path = Path(destination)
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Usa streaming de S3 para no cargar todo en memoria
        resp = self._client.get_object(Bucket=bucket, Key=file_id)
        body: BufferedReader = resp["Body"]

        with open(dst_path, "wb") as f:
            for chunk in iter(lambda: body.read(1024 * 1024), b""):  # 1MB chunks
                f.write(chunk)
        return dst_path

    def _generate_presigned_url(
        self, file_id: str, expires_in: int = 3600, bucket: str | None = None
    ) -> str:
        """
        Genera URL firmada temporal para descarga directa desde el cliente.

        Args:
            file_id: Key del archivo en S3
            expires_in: Tiempo de expiración en segundos (default: 1 hora)
            bucket: Bucket personalizado (opcional)

        Returns:
            URL firmada temporal
        """
        bucket = self._get_bucket(bucket)
        return self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": file_id},
            ExpiresIn=expires_in,
        )

    def get_public_url(self, file_id: str, bucket: str | None = None) -> str:
        """
        Genera la URL pública del archivo desde su key.

        Args:
            file_id: Key del archivo en S3
            bucket: Bucket personalizado (opcional)

        Returns:
            URL pública del archivo
        """
        bucket = self._get_bucket(bucket)

        # Si hay endpoint_url configurado (DigitalOcean Spaces o S3-compatible)
        if self._settings.s3_endpoint_url:
            # Para DigitalOcean Spaces: https://bucket.region.digitaloceanspaces.com/key
            # O endpoint personalizado: https://endpoint/bucket/key
            endpoint = self._settings.s3_endpoint_url.rstrip("/")
            return f"{endpoint}/{bucket}/{file_id}"

        # Para AWS S3: https://bucket.s3.region.amazonaws.com/key
        region = self._settings.aws_region_name
        return f"https://{bucket}.s3.{region}.amazonaws.com/{file_id}"

    async def save_file(
        self,
        file_data: bytes,
        file_name: str,
        folder: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Guarda un archivo en S3 y retorna su key.

        Args:
            file_data: Datos binarios del archivo
            file_name: Nombre del archivo
            folder: Carpeta destino (opcional, se usa como prefijo en la key)
            metadata: Metadata adicional del archivo

        Returns:
            Key del archivo guardado en S3
        """
        bucket = self._get_bucket()
        key = self._build_key(file_name, folder)

        put_params = {
            "Bucket": bucket,
            "Key": key,
            "Body": file_data,
        }

        if metadata:
            metadata_dict = {k: str(v) for k, v in metadata.items()}
            put_params["Metadata"] = metadata_dict

        await asyncio.to_thread(self._client.put_object, **put_params)
        return key

    async def get_file(self, file_id: str) -> bytes:
        """
        Obtiene los datos de un archivo por su key.

        Args:
            file_id: Key del archivo en S3

        Returns:
            Datos binarios del archivo
        """
        bucket = self._get_bucket()

        def _get_object():
            try:
                resp = self._client.get_object(Bucket=bucket, Key=file_id)
                return resp["Body"].read()
            except Exception as e:
                import traceback

                print(e)
                traceback.print_exc()
                return None

        return await asyncio.to_thread(_get_object)

    async def delete_file(self, file_id: str) -> bool:
        """
        Elimina un archivo de S3.

        Args:
            file_id: Key del archivo en S3

        Returns:
            True si se eliminó correctamente
        """
        bucket = self._get_bucket()

        def _delete_object():
            try:
                self._client.delete_object(Bucket=bucket, Key=file_id)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_delete_object)

    async def file_exists(self, file_id: str) -> bool:
        """
        Verifica si un archivo existe en S3.

        Args:
            file_id: Key del archivo en S3

        Returns:
            True si el archivo existe
        """
        bucket = self._get_bucket()

        def _head_object():
            try:
                self._client.head_object(Bucket=bucket, Key=file_id)
                return True
            except Exception:
                return False

        return await asyncio.to_thread(_head_object)

    def save_file_sync(
        self,
        file_data: bytes,
        file_name: str,
        folder: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Versión síncrona de save_file."""
        bucket = self._get_bucket()
        key = self._build_key(file_name, folder)

        put_params = {
            "Bucket": bucket,
            "Key": key,
            "Body": file_data,
        }

        if metadata:
            metadata_dict = {k: str(v) for k, v in metadata.items()}
            put_params["Metadata"] = metadata_dict

        self._client.put_object(**put_params)
        return key

    def get_file_sync(self, file_id: str) -> bytes:
        """Versión síncrona de get_file."""
        bucket = self._get_bucket()
        resp = self._client.get_object(Bucket=bucket, Key=file_id)
        return resp["Body"].read()

    def delete_file_sync(self, file_id: str) -> bool:
        """Versión síncrona de delete_file."""
        bucket = self._get_bucket()
        try:
            self._client.delete_object(Bucket=bucket, Key=file_id)
            return True
        except Exception:
            return False

    def file_exists_sync(self, file_id: str) -> bool:
        """Versión síncrona de file_exists."""
        bucket = self._get_bucket()
        try:
            self._client.head_object(Bucket=bucket, Key=file_id)
            return True
        except Exception:
            return False
