from abc import ABC, abstractmethod
from typing import Any

from src.domain.models.message import LLMResponse, Message


class LLMPort(ABC):
    """Port para servicios de Large Language Model (generación de texto)."""

    @abstractmethod
    async def generate_response(
        self,
        messages: list[Message],
        response_id: str | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_schema: dict[str, Any] | None = None,
        files: list[tuple[str, bytes, str]] | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Genera una respuesta usando el modelo de lenguaje.

        Args:
            messages: lista de mensajes de conversación
            response_id: ID de respuesta previa (opcional)
            system_prompt: Instrucciones del sistema
            temperature: Control de aleatoriedad (0-2)
            max_tokens: Máximo de tokens a generar
            json_schema: Schema JSON para respuestas estructuradas
            files: Lista opcional de archivos como tuplas (filename, file_data_bytes, mime_type)
            **kwargs: Parámetros adicionales específicos del proveedor

        Returns:
            LLMResponse con el texto generado y metadata

        Raises:
            AIProviderError: Si hay error en la generación
        """
        pass

    @abstractmethod
    async def generate_structured_response(
        self,
        messages: list[Message],
        response_format: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Genera una respuesta estructurada (JSON) según un schema.

        Args:
            messages: lista de mensajes de conversación
            response_format: Formato esperado de la respuesta (JSON Schema)
            system_prompt: Instrucciones del sistema
            **kwargs: Parámetros adicionales

        Returns:
            Dict con la respuesta estructurada
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor (openai, anthropic, google, etc.)"""
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Retorna información del modelo actual (nombre, versión, capacidades)"""
        pass
