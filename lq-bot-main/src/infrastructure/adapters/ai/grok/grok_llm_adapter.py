"""Adaptador LLM para Grok (X.AI)."""

import json
from datetime import datetime
from typing import Any

from openai import OpenAI

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort


class GrokLLMAdapter(LLMPort):
    """
    Implementación del port LLM usando Grok (X.AI).

    Grok usa una API compatible con OpenAI, por lo que podemos usar
    el cliente de OpenAI cambiando solo la base_url.
    """

    def __init__(
        self, api_key: str, model: str = "grok-beta", base_url: str = "https://api.x.ai/v1"
    ):
        """
        Inicializa el adaptador de Grok.

        Args:
            api_key: API key de Grok/X.AI
            model: Modelo a usar (grok-beta por defecto)
            base_url: URL base de la API de Grok
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.provider_name = "grok"

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
        Genera respuesta usando Grok API.

        Nota: Grok actualmente no soporta archivos, por lo que si se proporcionan
        archivos, se ignorarán y solo se usará el texto.
        """
        try:
            # Convertir mensajes de dominio a formato OpenAI
            grok_messages = self._convert_messages(messages, system_prompt)

            params = {
                "model": self.model,
                "messages": grok_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if json_schema:
                params["response_format"] = {"type": "json_object"}

            # Si hay archivos, advertir que no se soportan (pero no fallar)
            if files:
                # Grok no soporta archivos actualmente, solo usar el texto
                pass

            response = self.client.chat.completions.create(**params)

            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "completion_tokens": response.usage.completion_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                },
                created_at=datetime.now(),
            )

        except Exception as e:
            raise AIProviderError(
                f"Error en Grok LLM: {e!s}", provider="grok", original_error=e
            ) from e

    async def generate_structured_response(
        self,
        messages: list[Message],
        response_format: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Genera respuesta estructurada JSON."""
        response = await self.generate_response(
            messages=messages, system_prompt=system_prompt, json_schema=response_format, **kwargs
        )

        return json.loads(response.content)

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": ["text_generation", "json_mode", "streaming"],
        }

    def _convert_messages(
        self, messages: list[Message], system_prompt: str | None = None
    ) -> list[dict[str, str]]:
        """Convierte mensajes de dominio a formato compatible con Grok."""
        grok_msgs = []

        if system_prompt:
            grok_msgs.append({"role": "system", "content": system_prompt})

        for msg in messages:
            grok_msgs.append({"role": msg.role, "content": msg.content})

        return grok_msgs
