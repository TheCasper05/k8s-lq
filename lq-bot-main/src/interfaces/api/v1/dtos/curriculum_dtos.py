"""DTOs para endpoints de currículos."""

from pydantic import BaseModel, ConfigDict, Field

from src.domain.models.curriculum import Curriculum, CurriculumMetadata


class CurriculumCreateRequest(BaseModel):
    """Request para crear un currículo."""

    level: str = Field(
        ..., description="Nivel educativo (A1, A2, B1, B2, C1, C2)", min_length=2, max_length=2
    )
    language: str = Field(..., description="Idioma del currículo", min_length=1, max_length=50)
    topics: list[str] | None = Field(
        None, description="Lista opcional de temas a incluir en el currículo"
    )


class CurriculumCreateResponse(BaseModel):
    """Response para la creación de un currículo."""

    model_config = ConfigDict(from_attributes=True)

    curriculum: Curriculum = Field(..., description="Currículo generado")
    metadata: CurriculumMetadata = Field(..., description="Metadata de la generación")
