from rest_framework import serializers
from .validators import (
    validate_file_category,
    validate_file_size,
    validate_file_extension,
    validate_usage_path,
    validate_path_structure,
    validate_metadata,
)


class PresignedURLRequestSerializer(serializers.Serializer):
    """
    Serializer para validar la request de generación de URL prefirmada.
    """

    file_name = serializers.CharField(
        required=True,
        help_text="Nombre del archivo con extensión (ej: 'recording.mp3')",
    )
    file_category = serializers.CharField(
        required=True,
        help_text="Categoría del archivo: 'audio', 'image', 'pdf' o 'video'",
    )
    usage = serializers.CharField(
        required=True,
        help_text=(
            "Path completo donde se almacenará el archivo. "
            "Ejemplos:\n"
            "- activities/conversations/{uuid}/{resource_type}/{uuid}.mp3\n"
            "- institutions/{uuid}/{resource_type}/{uuid}.png\n"
            "- users/{uuid}/{resource_type}/{uuid}.pdf"
        ),
    )
    file_size = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="Tamaño del archivo en bytes",
    )
    metadata = serializers.JSONField(
        required=False,
        allow_null=True,
        help_text=(
            "Metadata opcional para el archivo (headers S3). "
            "Ejemplo: {'Content-Type': 'audio/mpeg', 'x-amz-meta-user-id': '123'}"
        ),
    )

    def validate_file_category(self, value: str) -> str:
        """
        Valida que la categoría sea una de las permitidas.
        """
        validate_file_category(value)
        return value

    def validate_usage(self, value: str) -> str:
        """
        Valida el formato y estructura del path de usage.
        """
        # Validar formato básico y seguridad
        validate_usage_path(value)

        # Validar estructura del path según contexto
        validate_path_structure(value)

        return value

    def validate_metadata(self, value: dict) -> dict:
        """
        Valida que las metadata keys sean permitidas.
        """
        if value is None:
            return {}

        validate_metadata(value)
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Validaciones cruzadas entre campos.
        """
        file_name = attrs.get("file_name")
        file_category = attrs.get("file_category")
        file_size = attrs.get("file_size")

        # Validar extensión del archivo
        validate_file_extension(file_name, file_category)

        # Validar tamaño por categoría
        validate_file_size(file_size, file_category)

        # Asegurar que metadata sea un dict (no None)
        if "metadata" not in attrs or attrs["metadata"] is None:
            attrs["metadata"] = {}

        return attrs


class PresignedDownloadURLRequestSerializer(serializers.Serializer):
    """
    Serializer para validar la request de generación de URL prefirmada de descarga.
    """

    file_path = serializers.CharField(
        required=True,
        help_text=(
            "Path completo del archivo en S3. "
            "Ejemplos:\n"
            "- activities/conversations/{uuid}/messages/{uuid}.mp3\n"
            "- users/{uuid}/avatars/{uuid}.jpg"
        ),
    )
    force_download = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Si es True, fuerza la descarga del archivo en lugar de mostrarlo en el navegador",
    )
    expiration = serializers.IntegerField(
        required=False,
        min_value=60,
        max_value=3600,
        help_text="Tiempo de expiración de la URL en segundos (60-3600). Por defecto 3600 (1 hora)",
    )

    def validate_file_path(self, value: str) -> str:
        """
        Valida el formato y estructura del file_path.
        """
        # Validar formato básico y seguridad
        validate_usage_path(value)

        # Validar estructura del path según contexto
        validate_path_structure(value)

        return value
