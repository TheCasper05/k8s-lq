"""Endpoints para generación de escenarios."""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.use_cases.create_scenario_use_case import CreateScenarioUseCase
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.interfaces.api.auth import verify_token
from src.interfaces.api.v1.dtos.scenario_dtos import (
    ScenarioCreateRequest,
    ScenarioCreateResponse,
)

router = APIRouter(prefix="/scenario", tags=["scenario"])


@router.post("/create", response_model=ScenarioCreateResponse, status_code=200)
@inject
async def create_scenario(
    request: ScenarioCreateRequest,
    api_key: str = Depends(verify_token),
    use_case: CreateScenarioUseCase = Depends(Provide[Container.create_scenario_use_case]),
) -> ScenarioCreateResponse:
    """
    Genera un escenario de conversación basado en la solicitud del usuario.

    Args:
        request: Datos de la petición (user_request, temperature opcional, max_tokens opcional)
        api_key: API key validada
        use_case: Caso de uso de creación de escenarios inyectado

    Returns:
        ScenarioCreateResponse con el escenario generado y metadata

    Raises:
        HTTPException: Si hay error al generar el escenario
    """
    try:
        scenario, scenario_metadata = await use_case.execute(
            user_request=request.user_request,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ScenarioCreateResponse(
            scenario=scenario,
            metadata=scenario_metadata,
        )

    except AIProviderError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar escenario: {e!s}") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {e!s}") from e
