"""Endpoints para traducción."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.batch_translate_use_case import BatchTranslateUseCase
from src.application.use_cases.translate_message_use_case import TranslateMessageUseCase
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.interfaces.api.auth import verify_token
from src.interfaces.api.v1.dtos.translation_dtos import (
    BatchTranslationResponse,
    TranslationRequest,
    TranslationResponse,
)

router = APIRouter(prefix="/translation", tags=["translation"])


@router.post("/translations", status_code=200)
@inject
async def translate(
    request: TranslationRequest,
    api_key: str = Depends(verify_token),
    batch_use_case: BatchTranslateUseCase = Depends(Provide[Container.batch_translate_use_case]),
    message_use_case: TranslateMessageUseCase = Depends(
        Provide[Container.translate_message_use_case]
    ),
) -> TranslationResponse | BatchTranslationResponse:
    """
    Endpoint unificado para traducción.

    Puede recibir:
    - `message_text`: Texto simple a traducir → usa TranslateMessageUseCase
    - `data`: Array de objetos JSON con id y texto → usa BatchTranslateUseCase

    Args:
        request: Datos de la petición (message_text o data)
        api_key: API key validada
        batch_use_case: Caso de uso para traducción batch
        message_use_case: Caso de uso para traducción de mensaje simple

    Returns:
        TranslationResponse si es texto simple, BatchTranslationResponse si es batch

    Raises:
        HTTPException: Si hay error al traducir
    """
    try:
        if request.data is not None:
            # Usar BatchTranslateUseCase
            result, llm_response = await batch_use_case.execute(
                data=request.data,
                target_language=request.target_language,
                native_language=request.native_language,
            )

            # Extraer información del resultado
            metadata = llm_response.metadata or {}
            tokens_used = llm_response.tokens_used or metadata.get("total_tokens")

            return BatchTranslationResponse(
                translations=result.get("translations", []),
                provider=llm_response.provider,
                model=llm_response.model,
                tokens_used=tokens_used,
            )
        else:
            # Usar TranslateMessageUseCase
            if request.message_text is None:
                raise HTTPException(
                    status_code=400, detail="Debe proporcionarse 'message_text' o 'data'"
                )

            translation_text, llm_response = await message_use_case.execute(
                message_text=request.message_text,
                target_language=request.target_language,
                native_language=request.native_language,
            )

            metadata = llm_response.metadata or {}
            tokens_used = llm_response.tokens_used or metadata.get("total_tokens")

            return TranslationResponse(
                translation=translation_text,
                provider=llm_response.provider,
                model=llm_response.model,
                tokens_used=tokens_used,
            )

    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al traducir: {e!s}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e
