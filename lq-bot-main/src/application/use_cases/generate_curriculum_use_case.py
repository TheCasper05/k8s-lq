"""Caso de uso para generar currículos educativos completos."""

import json
from datetime import datetime

from src.domain.models.curriculum import Curriculum, CurriculumMetadata, Submodule
from src.domain.models.message import Message
from src.domain.ports.ai.llm_port import LLMPort
from src.prompt_manager.manager import PromptManager


class CurriculumGeneratorUseCase:
    """Caso de uso: Generar un currículo educativo completo con unidades, objetivos y subtemas."""

    def __init__(self, llm: LLMPort, prompt_manager: PromptManager):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar currículos
            prompt_manager: Gestor de prompts para obtener templates
        """
        self.llm = llm
        self.prompt_manager = prompt_manager

    async def execute(
        self,
        level: str,
        language: str,
        topics: list[str] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> tuple[Curriculum, CurriculumMetadata]:
        """
        Ejecuta el caso de uso: genera un currículo completo.

        Args:
            level: Nivel educativo (A1, A2, B1, B2, C1, C2)
            language: Idioma del currículo
            topics: Lista opcional de temas a incluir
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (Curriculum generado, CurriculumMetadata con información de la generación)

        Raises:
            AIProviderError: Si hay un error al generar el currículo
        """
        # Construir descripción del curso basada en level, language y topics
        description_parts = [f"Curso de {language} nivel {level}"]
        if topics:
            description_parts.append(f"sobre los siguientes temas: {', '.join(topics)}")
        description = ". ".join(description_parts) + "."

        # Obtener el prompt del sistema desde archivo
        system_prompt = self.prompt_manager.render(
            "curriculums",
            "create_system",
            version="v1",
        )

        # Obtener el prompt del usuario
        user_prompt = self.prompt_manager.render(
            "curriculums",
            "create_user",
            version="v1",
            description=description,
            language=language,
        )

        # Obtener el schema de respuesta (es un dict, no se renderiza)
        response_schema = self.prompt_manager.render(
            "curriculums",
            "create_response_schema",
            version="v1",
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
        try:
            result = json.loads(response.content)
        except json.JSONDecodeError as err:
            # Si no es JSON válido, intentar extraerlo del contenido
            content = response.content.strip()
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    result = json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    raise ValueError(
                        f"No se pudo parsear la respuesta como JSON: {response.content}"
                    ) from err
            else:
                raise ValueError(
                    f"No se pudo parsear la respuesta como JSON: {response.content}"
                ) from err

        # Construir el objeto Curriculum desde el dict
        curriculum = Curriculum(
            name=result.get("name", ""),
            description=result.get("description", ""),
            submodules=[
                Submodule(
                    name=submodule.get("name", ""),
                    scenarios=submodule.get("scenarios", []),
                )
                for submodule in result.get("submodules", [])
            ],
        )

        # Extraer información de metadata del LLMResponse
        metadata = response.metadata or {}
        tokens_used = response.tokens_used or metadata.get("total_tokens")

        # Construir metadata
        curriculum_metadata = CurriculumMetadata(
            provider=response.provider,
            model=response.model,
            tokens_used=tokens_used,
            finish_reason=response.finish_reason,
        )

        return curriculum, curriculum_metadata
