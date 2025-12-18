"""Caso de uso para generar respuestas de texto usando LLM."""

from datetime import datetime
from typing import Any

from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort


class GenerateConversationSuggestionsUseCase:
    """Caso de uso: Generar sugerencias de palabras dado un contexto de conversación."""

    def __init__(self, llm: LLMPort):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar respuestas
        """
        self.llm = llm

    async def execute(
        self,
        user_message: str,
        system_prompt: str | None = None,
        response_schema: dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        Ejecuta el caso de uso: genera sugerencias de palabras.

        Args:
            user_message: Mensaje del usuario
            system_prompt: Prompt del sistema (instrucciones)
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            LLMResponse con las sugerencias generadas

        Raises:
            AIProviderError: Si hay un error al generar las sugerencias
        """
        messages = []

        user_msg = Message(
            role="user", content=user_message, timestamp=datetime.now(), metadata=None
        )
        messages.append(user_msg)

        response = await self.llm.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            json_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response
