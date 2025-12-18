"""Caso de uso para traducir estructuras JSON en batch."""

from datetime import datetime
from typing import Any

from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort
from src.prompt_manager.manager import PromptManager


class BatchTranslateUseCase:
    """Caso de uso: Traducir un array de objetos JSON manteniendo su estructura."""

    def __init__(self, llm: LLMPort, prompt_manager: PromptManager):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar traducciones
            prompt_manager: Gestor de prompts para obtener templates
        """
        self.llm = llm
        self.prompt_manager = prompt_manager

    async def execute(
        self,
        data: list[dict[str, Any]],
        target_language: str,
        native_language: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 16000,
    ) -> tuple[dict[str, Any], LLMResponse]:
        """
        Ejecuta el caso de uso: traduce un array de objetos JSON.

        Args:
            data: Array de objetos con id y texto a traducir
            target_language: Idioma destino para la traducción
            native_language: Idioma nativo (opcional, para contexto)
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (dict con las traducciones, LLMResponse con metadata)

        Raises:
            AIProviderError: Si hay un error al generar la traducción
        """
        # Obtener el schema de respuesta (es un dict, no se renderiza)
        response_schema = self.prompt_manager.render(
            "translations", "create_response_schema", version="v1"
        )

        # Obtener el prompt del sistema
        system_prompt = self.prompt_manager.render(
            "translations",
            "create_system",
            version="v1",
        )

        # Obtener el prompt del usuario
        user_prompt = self.prompt_manager.render(
            "translations",
            "create_user",
            version="v1",
            learning_units=data,
            language=target_language,
        )

        messages = []

        # Crear mensaje del usuario
        user_msg = Message(
            role="user",
            content=user_prompt,
            timestamp=datetime.now(),
            metadata=None,
        )

        messages.append(user_msg)

        # Generar respuesta estructurada
        response = await self.llm.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            json_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parsear la respuesta JSON
        import json

        try:
            result = json.loads(response.content)
            return result, response
        except json.JSONDecodeError as err:
            # Si no es JSON válido, intentar extraerlo del contenido
            # Esto puede pasar si el LLM añade texto adicional
            content = response.content.strip()
            # Buscar el JSON en el contenido
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    result = json.loads(content[start_idx:end_idx])
                    return result, response
                except json.JSONDecodeError:
                    raise ValueError(
                        f"No se pudo parsear la respuesta como JSON: {response.content}"
                    ) from err
            raise ValueError(
                f"No se pudo parsear la respuesta como JSON: {response.content}"
            ) from err
