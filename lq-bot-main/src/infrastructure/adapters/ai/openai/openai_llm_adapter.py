import base64
import json
from datetime import datetime
from typing import Any

from openai import AsyncOpenAI

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort


class OpenAILLMAdapter(LLMPort):
    """Implementación del port LLM usando OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.provider_name = "openai"

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
        """Genera respuesta usando OpenAI API."""
        try:
            # Convertir mensajes de dominio a formato OpenAI
            openai_messages = self._convert_messages(messages, system_prompt, files)

            params = {
                "model": self.model,
                "previous_response_id": response_id,
                # "messages": openai_messages,
                "input": openai_messages,
                "temperature": temperature,
                # "max_tokens": max_tokens,
                "max_output_tokens": max_tokens,
            }

            if json_schema:
                # params["response_format"] = {"type": "json_schema", "json_schema": json_schema}
                params["text"] = {
                    "format": {
                        "type": "json_schema",
                        "name": "response_schema",
                        "schema": json_schema,
                    }
                }

            # response = await asyncio.to_thread(self.client.chat.completions.create, **params)
            response = await self.client.responses.create(**params)

            return LLMResponse(
                # content=response.choices[0].message.content,
                content=response.output_text,
                response_id=response.id,
                provider=self.provider_name,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                # finish_reason=response.choices[0].finish_reason,
                incomplete_reason=response.incomplete_details,
                metadata={
                    "completion_tokens": response.usage.output_tokens,
                    "prompt_tokens": response.usage.input_tokens,
                },
                created_at=datetime.now(),
            )

        except Exception as e:
            raise AIProviderError(
                f"Error en OpenAI LLM: {e!s}", provider="openai", original_error=e
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
            "capabilities": ["text_generation", "structured_output", "json_mode"],
        }

    def _convert_messages(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        files: list[tuple[str, bytes, str]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Convierte mensajes de dominio a formato OpenAI.

        Si hay archivos, los convierte a base64 y los agrega al contenido del mensaje
        en el formato requerido por OpenAI (input_file e input_text).
        """
        openai_msgs = []

        if system_prompt:
            openai_msgs.append({"role": "system", "content": system_prompt})

        for msg in messages:
            # Si hay archivos, construir contenido con archivos y texto
            if files and msg.role == "user":
                content = []

                # Agregar archivos primero
                for filename, file_data, mime_type in files:
                    base64_string = base64.b64encode(file_data).decode("utf-8")
                    content.append(
                        {
                            "type": "input_file",
                            "filename": filename,
                            "file_data": f"data:{mime_type};base64,{base64_string}",
                        }
                    )

                # Agregar texto si existe
                if msg.content:
                    content.append(
                        {
                            "type": "input_text",
                            "text": msg.content,
                        }
                    )

                openai_msgs.append({"role": msg.role, "content": content})
            else:
                # Mensaje normal sin archivos
                openai_msgs.append({"role": msg.role, "content": msg.content})

        return openai_msgs
