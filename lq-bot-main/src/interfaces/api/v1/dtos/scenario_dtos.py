"""DTOs para endpoints de escenarios."""

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.scenario import Scenario, ScenarioMetadata


class ScenarioCreateRequest(BaseModel):
    """Request para crear un escenario."""

    user_request: str = Field(
        ..., description="Solicitud del usuario para crear el escenario", min_length=1
    )
    temperature: float = Field(
        default=0.7, description="Temperatura para la generación (0-2)", ge=0.0, le=2.0
    )
    max_tokens: int = Field(default=2000, description="Máximo de tokens a generar", ge=1, le=16000)


class ScenarioCreateResponse(BaseModel):
    """Response para la creación de un escenario."""

    model_config = ConfigDict(from_attributes=True)

    scenario: Scenario = Field(..., description="Escenario generado")
    metadata: ScenarioMetadata = Field(..., description="Metadata de la generación")
