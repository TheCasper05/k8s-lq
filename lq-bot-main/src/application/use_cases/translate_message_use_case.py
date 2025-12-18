"""Caso de uso para traducir mensajes simples."""

import json
from datetime import datetime

from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort
from src.prompt_manager.manager import PromptManager


class TranslateMessageUseCase:
    """Caso de uso: Traducir un mensaje simple a un idioma destino."""

    def __init__(self, llm: LLMPort, prompt_manager: PromptManager):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar traducciones
        """
        self.llm = llm

        self.prompt_manager = prompt_manager

    async def execute(
        self,
        message_text: str,
        target_language: str,
        native_language: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> tuple[dict[str, str], LLMResponse]:
        """
        Ejecuta el caso de uso: traduce un mensaje simple.

        Args:
            message_text: Texto a traducir
            target_language: Idioma destino para la traducción
            native_language: Idioma nativo (opcional, para contexto)
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (dict con id y translation, LLMResponse con metadata)

        Raises:
            AIProviderError: Si hay un error al generar la traducción
        """
        system_prompt = self.prompt_manager.render("translations", "create_system", "v1")

        # Convertir message_text a formato de array para el prompt
        learning_units = [{"id": "1", "word": message_text}]
        user_prompt = self.prompt_manager.render(
            "translations",
            "create_user",
            "v1",
            learning_units=learning_units,
            language=target_language,
        )

        response_schema = self.prompt_manager.render("translations", "create_response_schema", "v1")

        messages = []

        # Crear mensaje del usuario usando el prompt renderizado
        user_msg = Message(
            role="user",
            content=user_prompt,
            timestamp=datetime.now(),
            metadata=None,
        )
        messages.append(user_msg)

        # Generar respuesta
        response = await self.llm.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            json_schema=response_schema,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parsear la respuesta JSON
        try:
            result = json.loads(response.content.strip())
            translation_json = result["translations"][0]
        except (json.JSONDecodeError, KeyError, IndexError) as err:
            # Si no es JSON válido, intentar extraerlo del contenido
            content = response.content.strip()
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    result = json.loads(content[start_idx:end_idx])
                    translation_json = result["translations"][0]
                except (json.JSONDecodeError, KeyError, IndexError):
                    raise ValueError(
                        f"No se pudo parsear la respuesta como JSON: {response.content}"
                    ) from err
            else:
                raise ValueError(
                    f"No se pudo parsear la respuesta como JSON: {response.content}"
                ) from err

        return translation_json, response
