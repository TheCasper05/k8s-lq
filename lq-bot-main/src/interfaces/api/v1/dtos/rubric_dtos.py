"""DTOs para endpoints de rúbricas."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.domain.models.rubric import (
    Rubric,
    RubricGrade,
    RubricGradeMetadata,
    RubricMetadata,
)


class RubricCreateRequest(BaseModel):
    """Request para crear una rúbrica."""

    text: str | None = Field(
        None, description="Explicación opcional del profesor sobre las métricas de evaluación"
    )
    url: str | None = Field(
        None,
        description="URL opcional del archivo que contiene información adicional. Si se proporciona, se asume que es creación con archivo.",
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "RubricCreateRequest":
        """Valida que al menos uno de los campos (text o url) esté presente."""
        if not self.text and not self.url:
            raise ValueError("Debe proporcionarse al menos uno de los campos: 'text' o 'url'")
        return self


class RubricCreateResponse(BaseModel):
    """Response para la creación de una rúbrica."""

    model_config = ConfigDict(from_attributes=True)

    rubric: Rubric = Field(..., description="Rúbrica generada")
    metadata: RubricMetadata = Field(..., description="Metadata de la generación")


class RubricGradeRequest(BaseModel):
    """Request para calificar una conversación con una rúbrica."""

    conversation: str = Field(..., description="Conversación entre el estudiante y el asistente")
    rubric: Rubric = Field(..., description="Rúbrica con las métricas a evaluar")


class RubricGradeResponse(BaseModel):
    """Response para la calificación de una conversación con rúbrica."""

    model_config = ConfigDict(from_attributes=True)

    grade: RubricGrade = Field(..., description="Calificación de la conversación")
    metadata: RubricGradeMetadata = Field(..., description="Metadata de la calificación")
