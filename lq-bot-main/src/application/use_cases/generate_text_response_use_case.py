"""Caso de uso para generar respuestas de texto usando LLM."""

from datetime import datetime

from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort


class GenerateTextResponseUseCase:
    """Caso de uso: Generar una respuesta de texto dado un contexto de conversación."""

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
        response_id: str | None = None,
        conversation_history: list[Message] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        Ejecuta el caso de uso: genera una respuesta de texto.

        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de mensajes previos
            system_prompt: Prompt del sistema (instrucciones)
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            LLMResponse con la respuesta generada

        Raises:
            AIProviderError: Si hay un error al generar la respuesta
        """
        messages = conversation_history or []

        user_msg = Message(
            role="user", content=user_message, timestamp=datetime.now(), metadata=None
        )
        messages.append(user_msg)

        response = await self.llm.generate_response(
            messages=messages,
            response_id=response_id,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response
