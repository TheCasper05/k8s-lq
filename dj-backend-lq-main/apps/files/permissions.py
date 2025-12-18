"""
Helpers para validar permisos de acceso a archivos en S3.

IMPORTANTE: Estos son helpers de ejemplo que DEBES adaptar a tu lógica de negocio.
Implementa las validaciones según tu modelo de permisos y relaciones entre usuarios y recursos.
"""

from typing import Dict
from django.core.exceptions import PermissionDenied


def validate_file_access_permission(user, path_info: Dict[str, str]) -> bool:
    """
    Valida que el usuario tenga permiso para acceder al archivo.

    Args:
        user: Usuario autenticado (request.user)
        path_info: Diccionario con información del path parseado por validate_path_structure()

    Returns:
        bool: True si tiene permiso, False en caso contrario

    Raises:
        PermissionDenied: Si el usuario no tiene permiso

    Example path_info structures:
        Activities:
        {
            "context": "activities",
            "activity_type": "conversations",
            "activity_id": "uuid",
            "resource_type": "messages",
            "file_path": "uuid.mp3"
        }

        Users:
        {
            "context": "users",
            "user_id": "uuid",
            "resource_type": "avatars",
            "file_path": "uuid.jpg"
        }

        Institutions:
        {
            "context": "institutions",
            "institution_id": "uuid",
            "resource_type": "logos",
            "file_path": "uuid.png"
        }
    """
    context = path_info.get("context")

    if context == "activities":
        return _validate_activity_access(user, path_info)
    elif context == "users":
        return _validate_user_access(user, path_info)
    elif context == "institutions":
        return _validate_institution_access(user, path_info)
    else:
        raise PermissionDenied(f"Contexto '{context}' no soportado")


def _validate_activity_access(user, path_info: Dict[str, str]) -> bool:
    """
    Valida acceso a archivos de activities.

    TODO: Implementar lógica específica según tu modelo de negocio.

    Ejemplos de validaciones que podrías implementar:
    - Verificar que el usuario sea participante de la conversación
    - Verificar que el usuario sea dueño de la actividad
    - Verificar que el usuario tenga un rol específico (teacher, student)
    - Verificar que la actividad pertenezca a una institución del usuario
    """
    activity_type = path_info.get("activity_type")
    activity_id = path_info.get("activity_id")
    resource_type = path_info.get("resource_type")

    # TODO: Implementa tu lógica aquí
    # Ejemplo básico (REEMPLAZAR con tu lógica real):

    # if activity_type == "conversations":
    #     # Verificar que el usuario sea parte de la conversación
    #     from apps.conversations.models import Conversation
    #     conversation = Conversation.objects.filter(id=activity_id).first()
    #     if not conversation:
    #         raise PermissionDenied("Conversación no encontrada")
    #
    #     if not conversation.participants.filter(id=user.id).exists():
    #         raise PermissionDenied("No tienes acceso a esta conversación")
    #
    # elif activity_type == "reading":
    #     # Verificar que el usuario tenga acceso a la actividad de lectura
    #     from apps.reading.models import ReadingActivity
    #     reading = ReadingActivity.objects.filter(id=activity_id).first()
    #     if not reading:
    #         raise PermissionDenied("Actividad de lectura no encontrada")
    #
    #     if reading.user_id != user.id and not user.is_teacher:
    #         raise PermissionDenied("No tienes acceso a esta actividad")

    # POR DEFECTO: Permitir acceso (CAMBIAR EN PRODUCCIÓN)
    # TODO: Cambiar a False y implementar validaciones reales
    return True


def _validate_user_access(user, path_info: Dict[str, str]) -> bool:
    """
    Valida acceso a archivos de users.

    TODO: Implementar lógica específica según tu modelo de negocio.

    Ejemplos de validaciones:
    - Verificar que el usuario sea dueño del archivo (user_id == user.id)
    - Permitir acceso a avatares públicos
    - Verificar permisos de admin para documentos privados
    """
    user_id = path_info.get("user_id")
    resource_type = path_info.get("resource_type")

    # TODO: Implementa tu lógica aquí
    # Ejemplo básico (REEMPLAZAR con tu lógica real):

    # if resource_type == "avatars":
    #     # Los avatares son públicos, cualquiera puede verlos
    #     return True
    #
    # elif resource_type in ["documents", "recordings"]:
    #     # Solo el dueño o admin pueden acceder
    #     if str(user.id) != user_id and not user.is_staff:
    #         raise PermissionDenied("No tienes acceso a este archivo")
    #
    # elif resource_type == "attachments":
    #     # Solo el dueño puede acceder
    #     if str(user.id) != user_id:
    #         raise PermissionDenied("No tienes acceso a este archivo")

    # POR DEFECTO: Solo el dueño puede acceder
    if str(user.id) != user_id:
        raise PermissionDenied("No tienes acceso a este archivo")

    return True


def _validate_institution_access(user, path_info: Dict[str, str]) -> bool:
    """
    Valida acceso a archivos de institutions.

    TODO: Implementar lógica específica según tu modelo de negocio.

    Ejemplos de validaciones:
    - Permitir acceso a logos/banners públicos
    - Verificar que el usuario pertenezca a la institución
    - Verificar roles (admin, teacher, student)
    """
    institution_id = path_info.get("institution_id")
    resource_type = path_info.get("resource_type")

    # TODO: Implementa tu lógica aquí
    # Ejemplo básico (REEMPLAZAR con tu lógica real):

    # if resource_type in ["logos", "banners"]:
    #     # Los logos y banners son públicos
    #     return True
    #
    # elif resource_type in ["documents", "media"]:
    #     # Verificar que el usuario pertenezca a la institución
    #     from apps.institutions.models import InstitutionMember
    #     is_member = InstitutionMember.objects.filter(
    #         institution_id=institution_id,
    #         user_id=user.id
    #     ).exists()
    #
    #     if not is_member and not user.is_staff:
    #         raise PermissionDenied("No perteneces a esta institución")

    # POR DEFECTO: Permitir acceso a recursos públicos
    if resource_type in ["logos", "banners"]:
        return True

    # Para otros recursos, requiere implementación
    raise PermissionDenied(
        f"Validación de permisos no implementada para resource_type '{resource_type}'"
    )


def validate_file_upload_permission(user, path_info: Dict[str, str]) -> bool:
    """
    Valida que el usuario tenga permiso para SUBIR un archivo.

    Similar a validate_file_access_permission pero para uploads.
    Puede tener reglas diferentes (ej: solo admins pueden subir logos de instituciones).

    Args:
        user: Usuario autenticado (request.user)
        path_info: Diccionario con información del path parseado

    Returns:
        bool: True si tiene permiso

    Raises:
        PermissionDenied: Si el usuario no tiene permiso
    """
    context = path_info.get("context")

    # TODO: Implementar validaciones específicas para upload
    # Por ahora, usar las mismas reglas que para acceso
    return validate_file_access_permission(user, path_info)
