"""Endpoints para generación de chat."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.generate_text_response_use_case import (
    GenerateTextResponseUseCase,
)
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.interfaces.api.v1.dtos.chat_dtos import ChatMessageRequest, ChatMessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/generate", response_model=ChatMessageResponse, status_code=200)
@inject
async def generate_text_response(
    request: ChatMessageRequest,
    use_case: GenerateTextResponseUseCase = Depends(
        Provide[Container.generate_text_response_use_case]
    ),
) -> ChatMessageResponse:
    """
    Genera una respuesta de texto usando LLM.

    Args:
        request: Datos de la petición
        use_case: Caso de uso inyectado

    Returns:
        Respuesta generada

    Raises:
        HTTPException: Si hay error al generar la respuesta
    """
    try:
        response = await use_case.execute(
            user_message=request.message,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ChatMessageResponse(
            content=response.content,
            provider=response.provider,
            model=response.model,
            tokens_used=response.tokens_used,
            finish_reason=response.finish_reason,
        )

    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar respuesta: {e!s}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e
