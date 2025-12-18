"""Endpoints para creación y calificación de rúbricas."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.create_rubric_use_case import CreateRubricUseCase
from src.application.use_cases.grade_rubric_use_case import GradeRubricUseCase
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.interfaces.api.auth import verify_token
from src.interfaces.api.v1.dtos.rubric_dtos import (
    RubricCreateRequest,
    RubricCreateResponse,
    RubricGradeRequest,
    RubricGradeResponse,
)

router = APIRouter(prefix="/rubric", tags=["rubric"])


@router.post("/create", response_model=RubricCreateResponse, status_code=200)
@inject
async def create_rubric(
    request: RubricCreateRequest,
    api_key: str = Depends(verify_token),
    use_case: CreateRubricUseCase = Depends(Provide[Container.create_rubric_use_case]),
) -> RubricCreateResponse:
    """
    Crea una rúbrica de evaluación basada en la explicación del profesor.

    Si se proporciona `url`, se asume que es creación con archivo.
    Si no se proporciona `url`, se asume que es creación solo con texto.

    Args:
        request: Datos de la petición (texto con explicación de métricas y url opcional)
        api_key: API key validada
        use_case: Caso de uso de creación de rúbricas inyectado

    Returns:
        RubricCreateResponse con la rúbrica generada y metadata

    Raises:
        HTTPException: Si hay error al generar la rúbrica
    """
    try:
        rubric, rubric_metadata = await use_case.execute(text=request.text, file_url=request.url)

        return RubricCreateResponse(
            rubric=rubric,
            metadata=rubric_metadata,
        )

    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar rúbrica: {e!s}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e


@router.post("/grade", response_model=RubricGradeResponse, status_code=200)
@inject
async def grade_rubric(
    request: RubricGradeRequest,
    api_key: str = Depends(verify_token),
    use_case: GradeRubricUseCase = Depends(Provide[Container.grade_rubric_use_case]),
) -> RubricGradeResponse:
    """
    Califica una conversación usando una rúbrica.

    Args:
        request: Datos de la petición (conversación y rúbrica)
        api_key: API key validada
        use_case: Caso de uso de calificación de rúbricas inyectado

    Returns:
        RubricGradeResponse con la calificación de la conversación y metadata

    Raises:
        HTTPException: Si hay error al generar la calificación
    """
    try:
        grade, grade_metadata = await use_case.execute(
            conversation=request.conversation,
            rubric=request.rubric,
        )

        return RubricGradeResponse(
            grade=grade,
            metadata=grade_metadata,
        )

    except AIProviderError as e:
        raise HTTPException(
            status_code=500, detail=f"Error al calificar conversación: {e!s}"
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e
