"""DTOs para endpoints de chat."""

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Request para generar una respuesta de texto."""

    message: str = Field(..., description="Mensaje del usuario", min_length=1, max_length=10000)
    system_prompt: str | None = Field(
        None, description="Prompt del sistema (instrucciones)", max_length=5000
    )
    temperature: float = Field(
        default=0.7, description="Temperatura para la generación (0-2)", ge=0.0, le=2.0
    )
    max_tokens: int = Field(default=1000, description="Máximo de tokens a generar", ge=1, le=4000)


class ChatMessageResponse(BaseModel):
    """Response con la respuesta generada."""

    content: str = Field(..., description="Contenido de la respuesta")
    provider: str = Field(..., description="Proveedor de IA usado")
    model: str = Field(..., description="Modelo usado")
    tokens_used: int = Field(..., description="Tokens consumidos")
    finish_reason: str = Field(..., description="Razón de finalización")
