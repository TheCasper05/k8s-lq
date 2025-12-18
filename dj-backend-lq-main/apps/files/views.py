from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from botocore.exceptions import ClientError
from .serializers import (
    PresignedURLRequestSerializer,
    PresignedDownloadURLRequestSerializer,
)
from .services import PresignedURLService
from .validators import validate_path_structure
from .permissions import (
    validate_file_access_permission,
    validate_file_upload_permission,
)


class PresignedURLView(APIView):
    """
    View para generar URLs prefirmadas para subir archivos a DigitalOcean Spaces.

    Esta vista permite a los clientes obtener URLs prefirmadas para subir archivos
    directamente a S3, evitando que el backend tenga que recibir y procesar los archivos.

    IMPORTANTE: Valida permisos del usuario antes de generar la URL.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Genera una URL prefirmada para subir un archivo.

        Request body:
        {
            "file_name": "recording.mp3",
            "file_category": "audio",
            "usage": "activities/conversations/{uuid}/messages/{uuid}.mp3",
            "file_size": 5242880,
            "metadata": {  // opcional
                "Content-Type": "audio/mpeg",
                "x-amz-meta-user-id": "123e4567-e89b-12d3-a456-426614174000",
                "x-amz-meta-sender-type": "user"
            }
        }

        Response:
        {
            "upload_url": "https://...",
            "headers": {
                "Content-Length": "5242880",
                "Content-Type": "audio/mpeg",
                "x-amz-acl": "public-read",
                "x-amz-meta-user-id": "123e4567-e89b-12d3-a456-426614174000",
                "x-amz-meta-sender-type": "user"
            },
            "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
            "expires_in": 3600
        }

        Nota: el cliente debe enviar todos los headers devueltos (incluido x-amz-acl)
        al realizar la petición PUT al bucket, para conservar el ACL configurado.

        Estructura de paths soportada:
        - activities/{activity_type}/{activity_id}/{resource_type}/{resource_id}.{ext}
        - institutions/{institution_id}/{resource_type}/{resource_id}.{ext}
        - users/{user_id}/{resource_type}/{resource_id}.{ext}
        """
        serializer = PresignedURLRequestSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        validated_data = serializer.validated_data

        try:
            # Validar permisos del usuario para subir el archivo
            path_info = validate_path_structure(validated_data["usage"])
            validate_file_upload_permission(request.user, path_info)

            # Generar URL prefirmada
            service = PresignedURLService()
            result = service.generate_presigned_url(
                file_path=validated_data["usage"],
                file_size=validated_data["file_size"],
                metadata=validated_data.get("metadata", {}),
            )

            return Response(result, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ClientError as e:
            return Response(
                {"error": f"Error al generar URL prefirmada: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"Error inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PresignedDownloadURLView(APIView):
    """
    View para generar URLs prefirmadas para descargar archivos de DigitalOcean Spaces.

    Esta vista valida permisos del usuario y genera URLs temporales para descargar archivos.
    El bucket S3 debe estar configurado como PRIVADO para que esta seguridad funcione.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Genera una URL prefirmada para descargar un archivo.

        Request body:
        {
            "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
            "force_download": false,  // opcional, default: false
            "expiration": 3600  // opcional, segundos (60-3600), default: 3600
        }

        Response:
        {
            "download_url": "https://...",
            "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
            "expires_in": 3600
        }
        """
        serializer = PresignedDownloadURLRequestSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        validated_data = serializer.validated_data

        try:
            # Validar permisos del usuario para acceder al archivo
            path_info = validate_path_structure(validated_data["file_path"])
            validate_file_access_permission(request.user, path_info)

            # Preparar parámetros opcionales
            force_download = validated_data.get("force_download", False)
            expiration = validated_data.get("expiration", None)

            # Extraer nombre del archivo del path
            file_name = validated_data["file_path"].split("/")[-1]

            # Configurar Content-Disposition si se requiere forzar descarga
            response_content_disposition = None
            if force_download:
                response_content_disposition = f'attachment; filename="{file_name}"'

            # Generar URL prefirmada de descarga
            service = PresignedURLService()
            result = service.generate_download_url(
                file_path=validated_data["file_path"],
                expiration=expiration,
                response_content_disposition=response_content_disposition,
            )

            return Response(result, status=status.HTTP_200_OK)

        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ClientError as e:
            return Response(
                {"error": f"Error al generar URL de descarga: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"error": f"Error inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
