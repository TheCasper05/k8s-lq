"""DTOs para endpoints de conversaciones."""

from pydantic import BaseModel, Field


class TextAnswerRequest(BaseModel):
    """Request para generar una respuesta de texto."""

    message: str = Field(..., description="Mensaje del usuario", min_length=1, max_length=10000)
    scenario_type: str = Field(..., description="Tipo de escenario")
    response_id: str | None = Field(
        None, description="ID de la respuesta para manejar historial de conversación"
    )
    theme: str = Field(None, description="Tema de la conversación")
    language: str = Field(None, description="Idioma de la conversación")
    assistant_role: str | None = Field(None, description="Rol del asistente")
    user_role: str | None = Field(None, description="Rol del usuario")
    potential_directions: str = Field(None, description="Posibles direcciones de la conversación")
    setting: str | None = Field(None, description="Configuración de la conversación")
    example: str | None = Field(None, description="Ejemplo de la conversación")
    additional_data: str = Field(None, description="Datos adicionales de la conversación")
    practice_topic: str | None = Field(None, description="Tema de la práctica")


class TextAnswerResponse(BaseModel):
    """Response para una respuesta de texto."""

    answer: str = Field(..., description="Contenido de la respuesta")
    response_id: str = Field(..., description="ID de la respuesta")
    model: str = Field(..., description="Modelo usado")
    input_tokens: int = Field(..., description="Tokens de entrada")
    output_tokens: int = Field(..., description="Tokens de salida")
    total_tokens: int = Field(..., description="Tokens totales")


class SuggestionsRequest(BaseModel):
    """Request para generar sugerencias de palabras."""

    assistant_message: str = Field(..., description="Mensaje del asistente")
    scenario_context: str = Field(..., description="Contexto del escenario")
    language: str = Field(..., description="Idioma de la conversación")


class SuggestionsResponse(BaseModel):
    """Response para sugerencias de palabras."""

    suggestions: list[str] = Field(..., description="Sugerencias de respuestas")
    model: str = Field(..., description="Modelo usado")
    tokens_used: int = Field(..., description="Tokens usados")


class ConversationStartRequest(BaseModel):
    """Request para iniciar una conversación."""

    scenario_type: str = Field(..., description="Tipo de escenario")
    language: str = Field(..., description="Idioma de la conversación")
    theme: str = Field(None, description="Tema de la conversación")
    assistant_role: str | None = Field(None, description="Rol del asistente")
    user_role: str | None = Field(None, description="Rol del usuario")
    potential_directions: str = Field(None, description="Posibles direcciones de la conversación")
    setting: str | None = Field(None, description="Configuración de la conversación")
    example: str | None = Field(None, description="Ejemplo de la conversación")
    additional_data: str = Field(None, description="Datos adicionales de la conversación")
    practice_topic: str | None = Field(None, description="Tema de la práctica")


class ConversationStartResponse(BaseModel):
    """Response para iniciar una conversación."""

    conversation_id: str = Field(..., description="ID único de la conversación")
    response_id: str = Field(..., description="ID de la respuesta de bienvenida")
    audio_url: str = Field(..., description="URL pública del archivo de audio de bienvenida")
    audio_key: str = Field(..., description="Key del archivo de audio en el storage")
    audio_duration: float = Field(..., description="Duración del audio en segundos")
    voice_used: str = Field(..., description="Voz usada para la síntesis")
    provider: str = Field(..., description="Proveedor de TTS usado")
    audio_format: str = Field(..., description="Formato del archivo de audio")
    filename: str = Field(..., description="Nombre del archivo")
