"""DTOs para endpoints de traducción."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class TranslationRequest(BaseModel):
    """Request híbrido para traducción (texto simple o estructura JSON)."""

    message_text: str | None = Field(
        None,
        description="Texto simple a traducir (opcional si se proporciona data)",
    )

    @field_validator("message_text")
    @classmethod
    def validate_message_text(cls, v: str | None) -> str | None:
        """Valida la longitud del message_text si se proporciona."""
        if v is not None:
            if len(v) < 1:
                raise ValueError("message_text debe tener al menos 1 carácter")
            if len(v) > 10000:
                raise ValueError("message_text no puede exceder 10000 caracteres")
        return v

    data: list[dict[str, Any]] | None = Field(
        None,
        description="Array de objetos JSON con id y texto a traducir (opcional si se proporciona message_text)",
    )
    target_language: str = Field(..., description="Idioma destino para la traducción", min_length=1)
    native_language: str | None = Field(
        None, description="Idioma nativo (opcional, para contexto)", min_length=1
    )

    @model_validator(mode="after")
    def validate_input(self) -> "TranslationRequest":
        """Valida que se proporcione message_text o data, pero no ambos."""
        message_text = self.message_text
        data = self.data

        if not message_text and not data:
            raise ValueError("Debe proporcionarse 'message_text' o 'data', pero no ambos")
        if message_text and data:
            raise ValueError("Solo se puede proporcionar 'message_text' o 'data', no ambos")

        return self

    @field_validator("data")
    @classmethod
    def validate_data_structure(cls, v: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
        """Valida que data tenga la estructura correcta (id y texto)."""
        if v is None:
            return v

        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Cada elemento de 'data' debe ser un objeto JSON")
            if "id" not in item:
                raise ValueError("Cada elemento de 'data' debe tener un campo 'id'")
            # El campo de texto puede ser cualquier clave excepto 'id'
            text_keys = [k for k in item if k != "id"]
            if not text_keys:
                raise ValueError(
                    "Cada elemento de 'data' debe tener al menos un campo de texto además de 'id'"
                )

        return v


class TranslationResponse(BaseModel):
    """Response para traducción simple (texto)."""

    translation: dict[str, str] = Field(..., description="Texto traducido")
    provider: str = Field(..., description="Proveedor de IA usado")
    model: str = Field(..., description="Modelo usado")
    tokens_used: int | None = Field(None, description="Tokens consumidos")


class BatchTranslationResponse(BaseModel):
    """Response para traducción batch (estructura JSON)."""

    translations: list[dict[str, str]] = Field(
        ..., description="Array de traducciones con id y translation"
    )
    provider: str = Field(..., description="Proveedor de IA usado")
    model: str = Field(..., description="Modelo usado")
    tokens_used: int | None = Field(None, description="Tokens consumidos")
