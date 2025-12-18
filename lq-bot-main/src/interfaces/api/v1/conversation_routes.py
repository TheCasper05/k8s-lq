from uuid import uuid4

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException, status as http_status

from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.ports.storage.file_storage_port import FileStoragePort
from src.domain.services.conversation_service import ConversationService
from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter
from src.interfaces.api.auth import verify_token

# from src.presentation.schemas.conversation_schemas import MessageResponse
from src.interfaces.api.v1.dtos.conversation_dtos import (
    ConversationStartRequest,
    ConversationStartResponse,
    SuggestionsRequest,
    SuggestionsResponse,
    TextAnswerRequest,
    TextAnswerResponse,
)

router = APIRouter(prefix="/conversation", tags=["conversation"])


# Dependency injection desde container
def get_conversation_service() -> ConversationService:
    return Container.conversation_service()


def get_storage_adapter() -> FileStoragePort:
    """Obtiene el storage adapter desde el container."""
    storage_factory = Container.storage_factory()
    return storage_factory.create_storage_adapter()


# @router.post("/message", response_model=MessageResponse)
# async def process_message(
#     audio: UploadFile = File(...),
#     language: str = "en",
#     service: ConversationService = Depends(get_conversation_service),
# ):
#     """Procesa un mensaje de voz y retorna respuesta."""

#     # Leer audio
#     audio_data = await audio.read()

#     # Usar servicio de dominio (desacoplado de implementación)
#     text_response, audio_response = await service.process_voice_message(
#         audio_data=audio_data,
#         conversation_context=[],  # Obtener de DB
#         language=language,
#     )

#     return MessageResponse(
#         text=text_response, audio_base64=base64.b64encode(audio_response).decode()
#     )


@router.post("/text_answer", response_model=TextAnswerResponse)
async def get_text_answer(
    request: TextAnswerRequest,
    service: ConversationService = Depends(get_conversation_service),
):
    """
    Obtiene una respuesta de texto.

    Args:
        request: Datos de la petición con mensaje y parámetros del escenario
        service: Servicio de conversación inyectado

    Returns:
        LLMResponse con la respuesta generada

    Raises:
        HTTPException: Si hay error al generar la respuesta
    """
    try:
        return await service.process_text_answer(
            request.message,
            request.response_id,
            request.scenario_type,
            request.theme,
            request.assistant_role,
            request.user_role,
            request.potential_directions,
            request.setting,
            request.example,
            request.additional_data,
            request.practice_topic,
        )
    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {e!s}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e


@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    request: SuggestionsRequest,
    service: ConversationService = Depends(get_conversation_service),
):
    """
    Obtiene sugerencias de palabras.

    Args:
        request: Datos de la petición con mensaje y parámetros del escenario
        service: Servicio de conversación inyectado

    Returns:
        LLMResponse con la respuesta generada

    Raises:
        HTTPException: Si hay error al generar la respuesta
    """
    try:
        return await service.process_suggestions(
            request.assistant_message,
            request.scenario_context,
            request.language,
        )
    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {e!s}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e


@router.post("/start", status_code=200, response_model=ConversationStartResponse)
@inject
async def start_conversation(
    request: ConversationStartRequest,
    api_key: str = Depends(verify_token),
    service: ConversationService = Depends(get_conversation_service),
    storage_adapter: FileStoragePort = Depends(get_storage_adapter),
) -> ConversationStartResponse:
    """
    Inicia una nueva conversación generando un audio de bienvenida.
    Funciona igual que get_text_answer pero con un mensaje fijo de inicio.

    Args:
        request: Datos de la petición con parámetros del escenario e idioma
        api_key: API key validada
        service: Servicio de conversación inyectado
        storage_adapter: Adaptador de storage para guardar el archivo

    Returns:
        ConversationStartResponse con la URL del archivo de audio y metadata

    Raises:
        HTTPException: Si hay error al iniciar la conversación
    """
    try:
        # Llamar al servicio para iniciar la conversación
        conversation_id, response_id, audio_output = await service.start_conversation(
            scenario_type=request.scenario_type,
            language=request.language,
            theme=request.theme,
            assistant_role=request.assistant_role,
            user_role=request.user_role,
            potential_directions=request.potential_directions,
            setting=request.setting,
            example=request.example,
            additional_data=request.additional_data,
            practice_topic=request.practice_topic,
        )

        # Generar resource_id único para el mensaje
        resource_id = str(uuid4())
        filename = f"{resource_id}.{audio_output.format}"

        # Construir la ruta según la nueva estructura: activities/conversations/{conversation_id}/messages/{resource_id}.{ext}
        folder = f"activities/conversations/{conversation_id}/messages"

        # Guardar archivo en storage
        file_key = await storage_adapter.save_file(
            file_data=audio_output.audio_data,
            file_name=filename,
            folder=folder,
            metadata={
                "conversation_id": conversation_id,
                "response_id": response_id,
                "resource_id": resource_id,
                "duration_seconds": str(audio_output.duration_seconds),
                "voice_used": audio_output.voice_used,
                "provider": audio_output.provider,
                "format": audio_output.format,
                "type": "welcome_audio",
                "resource_type": "messages",
            },
        )

        # Generar URL pública
        if isinstance(storage_adapter, Boto3StorageAdapter):
            audio_url = storage_adapter.get_public_url(file_key)
        else:
            # Para otros adapters, usar la key como URL temporal
            audio_url = file_key

        return ConversationStartResponse(
            conversation_id=conversation_id,
            response_id=response_id,
            audio_url=audio_url,
            audio_key=file_key,
            audio_duration=audio_output.duration_seconds,
            voice_used=audio_output.voice_used,
            provider=audio_output.provider,
            audio_format=audio_output.format,
            filename=resource_id,  # Solo el resource_id, sin extensión
        )

    except AIProviderError as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar conversación: {e!s}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {e!s}",
        ) from e
