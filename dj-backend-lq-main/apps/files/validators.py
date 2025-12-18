import re
from pathlib import Path
from django.core.exceptions import ValidationError
from .config import (
    FILE_UPLOAD_MAX_SIZES,
    FILE_UPLOAD_MAX_SIZE_GLOBAL,
    CATEGORY_EXTENSIONS,
    ALLOWED_CATEGORIES,
    ALLOWED_CONTEXTS,
    ACTIVITY_TYPES,
    RESOURCE_TYPES,
    ALLOWED_METADATA_KEYS,
)


def validate_file_category(category: str) -> None:
    """
    Valida que la categoría del archivo sea una de las permitidas.

    Args:
        category: Categoría del archivo a validar

    Raises:
        ValidationError: Si la categoría no está permitida
    """
    if category not in ALLOWED_CATEGORIES:
        raise ValidationError(
            f"Categoría '{category}' no permitida. "
            f"Categorías permitidas: {', '.join(ALLOWED_CATEGORIES)}"
        )


def validate_file_size(file_size: int, category: str) -> None:
    """
    Valida que el tamaño del archivo esté dentro de los límites permitidos
    para su categoría y del límite global.

    Args:
        file_size: Tamaño del archivo en bytes
        category: Categoría del archivo

    Raises:
        ValidationError: Si el tamaño excede los límites
    """
    max_size_global = FILE_UPLOAD_MAX_SIZE_GLOBAL
    max_sizes = FILE_UPLOAD_MAX_SIZES

    # Validar límite global
    if file_size > max_size_global:
        max_size_mb = max_size_global / (1024 * 1024)
        raise ValidationError(
            f"El tamaño del archivo ({file_size / (1024 * 1024):.2f} MB) "
            f"excede el límite global de {max_size_mb} MB"
        )

    # Validar límite por categoría
    max_size_category = max_sizes.get(category)
    if max_size_category and file_size > max_size_category:
        max_size_mb = max_size_category / (1024 * 1024)
        raise ValidationError(
            f"El tamaño del archivo ({file_size / (1024 * 1024):.2f} MB) "
            f"excede el límite de {max_size_mb} MB para la categoría '{category}'"
        )


def validate_file_extension(file_name: str, category: str) -> None:
    """
    Valida que la extensión del archivo sea válida para la categoría especificada.

    Args:
        file_name: Nombre del archivo con extensión
        category: Categoría del archivo

    Raises:
        ValidationError: Si la extensión no es válida para la categoría
    """
    file_ext = Path(file_name).suffix.lower()
    allowed_extensions = CATEGORY_EXTENSIONS.get(category, [])

    if not file_ext:
        raise ValidationError("El archivo debe tener una extensión")

    if file_ext not in allowed_extensions:
        raise ValidationError(
            f"La extensión '{file_ext}' no es válida para la categoría '{category}'. "
            f"Extensiones permitidas: {', '.join(allowed_extensions)}"
        )


def validate_usage_path(usage: str) -> None:
    """
    Valida el formato básico del path de usage (seguridad básica).

    Args:
        usage: Path de usage a validar

    Raises:
        ValidationError: Si el path no cumple con el formato requerido
    """
    if not usage:
        raise ValidationError("El campo 'usage' no puede estar vacío")

    # No debe empezar con /
    if usage.startswith("/"):
        raise ValidationError("El 'usage' no debe empezar con '/'")

    # No debe contener path traversal
    if ".." in usage:
        raise ValidationError("El 'usage' no puede contener '..' (path traversal)")

    # Debe contener al menos un separador
    if "/" not in usage:
        raise ValidationError("El 'usage' debe contener al menos un separador '/'")

    # No debe contener espacios
    if " " in usage:
        raise ValidationError("El 'usage' no puede contener espacios en blanco")

    # No debe contener caracteres especiales peligrosos
    dangerous_chars = ["\\", "|", "&", ";", "$", "`", "<", ">", "(", ")", "{", "}"]
    for char in dangerous_chars:
        if char in usage:
            raise ValidationError(
                f"El 'usage' no puede contener caracteres especiales como '{char}'"
            )


def validate_path_structure(usage: str) -> dict:
    """
    Valida que el path siga la estructura definida del bucket S3.

    Estructura esperada:
    - activities/{activity_type}/{activity_id}/{resource_type}/{resource_id}.{ext}
    - institutions/{institution_id}/{resource_type}/{resource_id}.{ext}
    - users/{user_id}/{resource_type}/{resource_id}.{ext}

    Args:
        usage: Path completo a validar

    Returns:
        dict: Diccionario con los componentes del path parseados

    Raises:
        ValidationError: Si la estructura no es válida
    """
    parts = usage.split("/")

    # Validar que tenga suficientes partes
    if len(parts) < 3:
        raise ValidationError(
            "El path debe tener al menos 3 niveles. "
            "Formato: {context}/{id}/{resource_type}/..."
        )

    context = parts[0]

    # Validar contexto
    if context not in ALLOWED_CONTEXTS:
        raise ValidationError(
            f"Contexto '{context}' no permitido. "
            f"Contextos permitidos: {', '.join(ALLOWED_CONTEXTS)}"
        )

    # Validar según el contexto
    if context == "activities":
        return _validate_activities_path(parts)
    elif context == "institutions":
        return _validate_institutions_path(parts)
    elif context == "users":
        return _validate_users_path(parts)


def _validate_activities_path(parts: list) -> dict:
    """
    Valida path para activities.
    Formato: activities/{activity_type}/{activity_id}/{resource_type}/{resource_id}.{ext}
    """
    if len(parts) < 5:
        raise ValidationError(
            "Path de activities debe tener formato: "
            "activities/{activity_type}/{activity_id}/{resource_type}/{resource_id}.{ext}"
        )

    context, activity_type, activity_id, resource_type, *file_parts = parts

    # Validar activity_type
    if activity_type not in ACTIVITY_TYPES:
        raise ValidationError(
            f"Activity type '{activity_type}' no permitido. "
            f"Tipos permitidos: {', '.join(ACTIVITY_TYPES)}"
        )

    # Validar resource_type
    allowed_resource_types = RESOURCE_TYPES["activities"].get(activity_type, [])
    if resource_type not in allowed_resource_types:
        raise ValidationError(
            f"Resource type '{resource_type}' no permitido para activity '{activity_type}'. "
            f"Tipos permitidos: {', '.join(allowed_resource_types)}"
        )

    # Validar formato de IDs (UUID)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(activity_id):
        raise ValidationError(f"Activity ID '{activity_id}' debe ser un UUID válido")

    return {
        "context": context,
        "activity_type": activity_type,
        "activity_id": activity_id,
        "resource_type": resource_type,
        "file_path": "/".join(file_parts) if file_parts else None,
    }


def _validate_institutions_path(parts: list) -> dict:
    """
    Valida path para institutions.
    Formato: institutions/{institution_id}/{resource_type}/{resource_id}.{ext}
    """
    if len(parts) < 4:
        raise ValidationError(
            "Path de institutions debe tener formato: "
            "institutions/{institution_id}/{resource_type}/{resource_id}.{ext}"
        )

    context, institution_id, resource_type, *file_parts = parts

    # Validar resource_type
    allowed_resource_types = RESOURCE_TYPES["institutions"]
    if resource_type not in allowed_resource_types:
        raise ValidationError(
            f"Resource type '{resource_type}' no permitido para institutions. "
            f"Tipos permitidos: {', '.join(allowed_resource_types)}"
        )

    # Validar formato de ID (UUID)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(institution_id):
        raise ValidationError(
            f"Institution ID '{institution_id}' debe ser un UUID válido"
        )

    return {
        "context": context,
        "institution_id": institution_id,
        "resource_type": resource_type,
        "file_path": "/".join(file_parts) if file_parts else None,
    }


def _validate_users_path(parts: list) -> dict:
    """
    Valida path para users.
    Formato: users/{user_id}/{resource_type}/{resource_id}.{ext}
    """
    if len(parts) < 4:
        raise ValidationError(
            "Path de users debe tener formato: "
            "users/{user_id}/{resource_type}/{resource_id}.{ext}"
        )

    context, user_id, resource_type, *file_parts = parts

    # Validar resource_type
    allowed_resource_types = RESOURCE_TYPES["users"]
    if resource_type not in allowed_resource_types:
        raise ValidationError(
            f"Resource type '{resource_type}' no permitido para users. "
            f"Tipos permitidos: {', '.join(allowed_resource_types)}"
        )

    # Validar formato de ID (UUID)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(user_id):
        raise ValidationError(f"User ID '{user_id}' debe ser un UUID válido")

    return {
        "context": context,
        "user_id": user_id,
        "resource_type": resource_type,
        "file_path": "/".join(file_parts) if file_parts else None,
    }


def validate_metadata(metadata: dict) -> None:
    """
    Valida que las metadata keys sean permitidas.

    Args:
        metadata: Diccionario de metadata a validar

    Raises:
        ValidationError: Si hay keys no permitidas
    """
    if not metadata:
        return

    if not isinstance(metadata, dict):
        raise ValidationError("Metadata debe ser un objeto JSON válido")

    for key in metadata.keys():
        if key not in ALLOWED_METADATA_KEYS:
            raise ValidationError(
                f"Metadata key '{key}' no permitida. "
                f"Keys permitidas: {', '.join(ALLOWED_METADATA_KEYS)}"
            )

    # Validar valores de metadata
    for key, value in metadata.items():
        if not isinstance(value, str):
            raise ValidationError(
                f"El valor de metadata '{key}' debe ser un string, recibió {type(value).__name__}"
            )

        # Limitar tamaño de valores (S3 tiene límite de 2KB por metadata value)
        if len(value) > 2048:
            raise ValidationError(
                f"El valor de metadata '{key}' excede el límite de 2048 caracteres"
            )
