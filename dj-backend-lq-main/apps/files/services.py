from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class PresignedURLService:
    """
    Servicio para generar URLs prefirmadas para DigitalOcean Spaces (S3).
    """

    def __init__(self):
        """Inicializa el cliente de S3 para DigitalOcean Spaces."""
        self.access_key_id = getattr(settings, "AWS_ACCESS_KEY_ID", "")
        self.secret_access_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", "")
        self.bucket_name = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
        self.endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", "")
        self.default_acl = getattr(settings, "AWS_DEFAULT_ACL", None)
        self.expire_seconds = getattr(
            settings, "DO_SPACES_PRESIGN_EXPIRE_SECONDS", 3600
        )

        # Validar configuración
        if not all([self.access_key_id, self.secret_access_key, self.bucket_name]):
            raise ImproperlyConfigured(
                "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY y "
                "AWS_STORAGE_BUCKET_NAME deben estar configurados"
            )

        # Crear cliente S3
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )

    def generate_presigned_url(
        self,
        file_path: str,
        file_size: int,
        metadata: Dict[str, str] | None = None,
        expiration: int | None = None,
    ) -> Dict[str, Any]:
        """
        Genera una URL prefirmada para subir un archivo a DigitalOcean Spaces.

        Args:
            file_path: Path completo del archivo en el bucket
            file_size: Tamaño del archivo en bytes
            metadata: Metadata opcional para el archivo (headers S3)
            expiration: Tiempo de expiración en segundos (opcional, usa default si no se proporciona)

        Returns:
            Dict con 'upload_url', 'headers' y 'file_path'

        Raises:
            ClientError: Si hay un error al generar la URL prefirmada
        """
        if expiration is None:
            expiration = self.expire_seconds

        if metadata is None:
            metadata = {}

        try:
            # Preparar parámetros para la URL prefirmada
            params = {
                "Bucket": self.bucket_name,
                "Key": file_path,
                "ContentLength": file_size,
            }

            # Separar metadata en parámetros S3 estándar y metadata personalizada
            s3_metadata = {}
            headers_to_return = {
                "Content-Length": str(file_size),
            }

            # Aplicar ACL por defecto si está configurado
            if self.default_acl:
                params["ACL"] = self.default_acl
                headers_to_return["x-amz-acl"] = self.default_acl

            for key, value in metadata.items():
                if key == "Content-Type":
                    # Content-Type es un parámetro estándar de S3
                    params["ContentType"] = value
                    headers_to_return["Content-Type"] = value
                elif key.startswith("x-amz-meta-"):
                    # Remover el prefijo x-amz-meta- para boto3
                    # boto3 lo agrega automáticamente
                    metadata_key = key.replace("x-amz-meta-", "")
                    s3_metadata[metadata_key] = value
                    headers_to_return[key] = value

            # Agregar metadata personalizada si existe
            if s3_metadata:
                params["Metadata"] = s3_metadata

            # Generar URL prefirmada
            presigned_url = self.s3_client.generate_presigned_url(
                "put_object",
                Params=params,
                ExpiresIn=expiration,
            )

            return {
                "upload_url": presigned_url,
                "headers": headers_to_return,
                "file_path": file_path,
                "expires_in": expiration,
            }
        except ClientError:
            # Re-lanzar el error original sin modificarlo
            raise

    def generate_download_url(
        self,
        file_path: str,
        expiration: int | None = None,
        response_content_type: str | None = None,
        response_content_disposition: str | None = None,
    ) -> Dict[str, Any]:
        """
        Genera una URL prefirmada para descargar un archivo de DigitalOcean Spaces.

        Args:
            file_path: Path completo del archivo en el bucket
            expiration: Tiempo de expiración en segundos (opcional, usa default si no se proporciona)
            response_content_type: Content-Type para la respuesta (opcional)
            response_content_disposition: Content-Disposition para forzar descarga (opcional)

        Returns:
            Dict con 'download_url', 'file_path' y 'expires_in'

        Raises:
            ClientError: Si hay un error al generar la URL prefirmada
        """
        if expiration is None:
            expiration = self.expire_seconds

        try:
            # Preparar parámetros para la URL prefirmada
            params = {
                "Bucket": self.bucket_name,
                "Key": file_path,
            }

            # Agregar parámetros opcionales para controlar la respuesta
            if response_content_type:
                params["ResponseContentType"] = response_content_type

            if response_content_disposition:
                params["ResponseContentDisposition"] = response_content_disposition

            # Generar URL prefirmada para GET
            presigned_url = self.s3_client.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expiration,
            )

            return {
                "download_url": presigned_url,
                "file_path": file_path,
                "expires_in": expiration,
            }
        except ClientError:
            # Re-lanzar el error original sin modificarlo
            raise
