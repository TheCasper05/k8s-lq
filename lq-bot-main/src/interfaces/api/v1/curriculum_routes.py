"""Endpoints para generación de currículos."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.generate_curriculum_use_case import CurriculumGeneratorUseCase
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.interfaces.api.auth import verify_token
from src.interfaces.api.v1.dtos.curriculum_dtos import (
    CurriculumCreateRequest,
    CurriculumCreateResponse,
)

router = APIRouter(prefix="/curriculum", tags=["curriculum"])


@router.post("/create", response_model=CurriculumCreateResponse, status_code=200)
@inject
async def create_curriculum(
    request: CurriculumCreateRequest,
    api_key: str = Depends(verify_token),
    use_case: CurriculumGeneratorUseCase = Depends(Provide[Container.generate_curriculum_use_case]),
) -> CurriculumCreateResponse:
    """
    Genera un currículo educativo completo basado en parámetros de entrada.

    Args:
        request: Datos de la petición (level, language, topics opcional)
        api_key: API key validada
        use_case: Caso de uso de generación de currículos inyectado

    Returns:
        CurriculumCreateResponse con el currículo generado y metadata

    Raises:
        HTTPException: Si hay error al generar el currículo
    """
    try:
        curriculum, curriculum_metadata = await use_case.execute(
            level=request.level,
            language=request.language,
            topics=request.topics,
        )

        return CurriculumCreateResponse(
            curriculum=curriculum,
            metadata=curriculum_metadata,
        )

    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar currículo: {e!s}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e
