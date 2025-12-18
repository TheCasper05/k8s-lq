"""Endpoints para procesamiento de audio."""

import re
from urllib.parse import urlparse
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status as http_status,
)
from fastapi.requests import Request

from src.application.use_cases.generate_audio_response_use_case import (
    GenerateAudioResponseUseCase,
)
from src.application.use_cases.generate_transcription_use_case import (
    GenerateTranscriptionUseCase,
)
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.ports.storage.file_storage_port import FileStoragePort
from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter
from src.interfaces.api.auth import verify_token
from src.interfaces.api.v1.dtos.audio_dtos import (
    CreateVoiceRequest,
    CreateVoiceResponse,
    TranscriptionRequest,
    TranscriptionResponse,
)

router = APIRouter(prefix="/audio", tags=["audio"])


def get_storage_adapter() -> FileStoragePort:
    """Obtiene el storage adapter desde el container."""
    storage_factory = Container.storage_factory()
    return storage_factory.create_storage_adapter()


def _is_url(source: str) -> bool:
    """
    Detecta si el source es una URL.

    Args:
        source: String que puede ser URL

    Returns:
        True si es URL
    """
    # Patrón simple para detectar URLs
    url_pattern = re.compile(
        r"^https?://|^s3://|^https://.*\.s3\.|^https://.*\.digitaloceanspaces\.com"
    )
    return bool(url_pattern.match(source.strip()))


async def _parse_json_body(http_request: Request) -> tuple[str | None, str | None]:
    """
    Parsea el body JSON de la request.

    Args:
        http_request: Request HTTP

    Returns:
        Tuple con (key, language)

    Raises:
        HTTPException: Si hay error al parsear el JSON
    """
    try:
        body = await http_request.json()
        request_data = TranscriptionRequest(**body)
        key = request_data.get_key()
        return key, request_data.language
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Error al parsear JSON body: {e!s}",
        ) from e


async def _parse_form_data(http_request: Request) -> tuple[bytes | None, str | None, str | None]:
    """
    Parsea el form data de la request.

    Args:
        http_request: Request HTTP

    Returns:
        Tuple con (file_bytes, key, language)
    """
    form = await http_request.form()
    file_bytes = None
    key_value = None
    language_value = None

    if "file" in form:
        file_obj = form["file"]
        if hasattr(file_obj, "read"):
            file_bytes = await file_obj.read()
        else:
            file_bytes = str(file_obj).encode() if file_obj else None

    # Priorizar 'key' sobre 'url' para mantener compatibilidad
    if "key" in form:
        key_value = form["key"]
    elif "url" in form:
        url_value = form["url"]
        # Si es una URL de S3/DigitalOcean Spaces, extraer la key
        if _is_url(url_value):
            parsed = urlparse(url_value)
            if parsed.scheme in ("s3", "https") and (
                ".s3." in url_value or "digitaloceanspaces.com" in url_value
            ):
                key_value = parsed.path.lstrip("/")
            else:
                # URL HTTP normal, mantenerla para descargar
                key_value = url_value
        else:
            # No es URL, asumir que es una key
            key_value = url_value

    if "language" in form:
        language_value = form["language"]

    return file_bytes, key_value, language_value


def _validate_inputs(file: bytes | None, key: str | None) -> None:
    """
    Valida que se proporcione file o key (pero no ambos).

    Args:
        file: Datos del archivo
        key: Key del archivo en storage o URL

    Raises:
        HTTPException: Si la validación falla
    """
    if not file and not key:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionarse 'file' o 'key', pero no ambos",
        )

    if file and key:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede proporcionar 'file' o 'key', no ambos",
        )


async def _get_audio_from_key(key_or_url: str, storage_adapter: FileStoragePort) -> bytes:
    """
    Obtiene audio desde una key del storage o desde una URL HTTP.

    Args:
        key_or_url: Key del archivo en storage o URL HTTP del archivo
        storage_adapter: Adaptador de storage

    Returns:
        Bytes del archivo de audio

    Raises:
        HTTPException: Si hay error al obtener el archivo
    """
    # Si es una URL HTTP/HTTPS normal (no S3/DO Spaces), descargar con httpx
    if _is_url(key_or_url) and not (".s3." in key_or_url or "digitaloceanspaces.com" in key_or_url):
        try:
            import httpx
        except ImportError as err:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="httpx no está instalado. Instálalo con: pip install httpx",
            ) from err

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(key_or_url)
            response.raise_for_status()
            return response.content

    # Es una key del storage (o URL de S3/DO Spaces que ya fue convertida a key)
    return await storage_adapter.get_file(key_or_url)


@router.post("/transcription", response_model=TranscriptionResponse, status_code=200)
@inject
async def transcribe_audio(
    http_request: Request,
    api_key: str = Depends(verify_token),
    use_case: GenerateTranscriptionUseCase = Depends(
        Provide[Container.generate_transcription_use_case]
    ),
    storage_adapter: FileStoragePort = Depends(get_storage_adapter),
) -> TranscriptionResponse:
    """
    Transcribe un archivo de audio a texto.

    Puede recibir:
    - JSON body con `key` (o `url` para compatibilidad) y `language` (opcional)
    - Form data con `file` y `language` (opcional)
    - Form data con `key` (o `url` para compatibilidad) y `language` (opcional)

    Args:
        http_request: Request HTTP para detectar content-type y parsear body
        api_key: API key validada
        use_case: Caso de uso de transcripción inyectado
        storage_adapter: Adaptador de storage para descargar archivos

    Returns:
        TranscriptionResponse con el texto transcrito

    Raises:
        HTTPException: Si hay error al transcribir el audio
    """
    try:
        # Detectar content-type y parsear
        content_type = http_request.headers.get("content-type", "").lower()
        key_value = None
        language_value = None
        file = None

        if "application/json" in content_type:
            key_value, language_value = await _parse_json_body(http_request)
        elif "multipart/form-data" in content_type:
            file, key_value, language_value = await _parse_form_data(http_request)
        else:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Content-Type debe ser 'application/json' o 'multipart/form-data'",
            )

        # Validar inputs
        _validate_inputs(file, key_value)

        # Obtener audio desde file o key
        audio_data = file if file else await _get_audio_from_key(key_value, storage_adapter)

        # Transcribir usando el caso de uso
        result = await use_case.execute(audio=audio_data, language=language_value)

        # Obtener el modelo del adaptador STT
        model_name = result.provider
        if hasattr(use_case.stt, "model"):
            model_name = use_case.stt.model

        return TranscriptionResponse(
            transcription=result.text,
            provider=result.provider,
            model=model_name,
        )

    except HTTPException:
        # Re-raise HTTPExceptions (ya tienen el formato correcto)
        raise
    except AIProviderError as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al transcribir audio: {e!s}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {e!s}",
        ) from e


@router.post("/create_voice", status_code=200, response_model=CreateVoiceResponse)
@inject
async def create_voice(
    request: CreateVoiceRequest,
    api_key: str = Depends(verify_token),
    use_case: GenerateAudioResponseUseCase = Depends(
        Provide[Container.generate_audio_response_use_case]
    ),
    storage_adapter: FileStoragePort = Depends(get_storage_adapter),
) -> CreateVoiceResponse:
    """
    Genera audio (TTS) desde texto.

    Args:
        request: Datos de la petición con texto y parámetros de voz
        api_key: API key validada
        use_case: Caso de uso de generación de audio inyectado
        storage_adapter: Adaptador de storage para guardar el archivo

    Returns:
        CreateVoiceResponse con la URL del archivo de audio y metadata

    Raises:
        HTTPException: Si hay error al generar el audio
    """
    try:
        # Generar audio usando el caso de uso
        audio_output = await use_case.execute(
            text=request.text,
            voice=request.voice,
            # language=request.language,
            audio_format=request.audio_format,  # type: ignore
            speed=request.speed,
        )

        # Generar resource_id único para el archivo
        resource_id = str(uuid4())
        filename = f"{resource_id}.{request.audio_format}"

        # Determinar la carpeta según el tipo de actividad
        if request.activity_type and request.activity_id:
            # Validar que si hay activity_type, también haya activity_id
            if not request.activity_id:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Si se proporciona 'activity_type', también debe proporcionarse 'activity_id'",
                )

            # Construir la ruta según el tipo de actividad
            if request.activity_type == "conversations":
                folder = f"activities/conversations/{request.activity_id}/messages"
                resource_type = "messages"
            elif request.activity_type == "listening":
                folder = f"activities/listening/{request.activity_id}/audios"
                resource_type = "audios"
            elif request.activity_type == "speaking":
                folder = f"activities/speaking/{request.activity_id}/recordings"
                resource_type = "recordings"
            else:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de actividad '{request.activity_type}' no soportado para audio",
                )
        else:
            # Si no se proporciona actividad, usar estructura legacy (compatibilidad hacia atrás)
            folder = "audio/tts"
            resource_type = "tts_audio"

        # Guardar archivo en storage
        file_key = await storage_adapter.save_file(
            file_data=audio_output.audio_data,
            file_name=filename,
            folder=folder,
            metadata={
                "duration_seconds": str(audio_output.duration_seconds),
                "voice_used": audio_output.voice_used,
                "provider": audio_output.provider,
                "format": audio_output.format,
                "speed": str(request.speed),
                "type": "tts_audio",
                "resource_type": resource_type,
                "resource_id": resource_id,
                "activity_type": request.activity_type or "none",
                "activity_id": request.activity_id or "none",
            },
        )

        # Generar URL pública
        if isinstance(storage_adapter, Boto3StorageAdapter):
            audio_url = storage_adapter.get_public_url(file_key)
        else:
            # Para otros adapters, usar la key como URL temporal
            audio_url = file_key

        return CreateVoiceResponse(
            url=audio_url,
            key=file_key,
            duration_seconds=audio_output.duration_seconds,
            voice_used=audio_output.voice_used,
            provider=audio_output.provider,
            format=audio_output.format,
            filename=resource_id,  # Solo el resource_id, sin extensión
        )

    except AIProviderError as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar audio: {e!s}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {e!s}",
        ) from e
