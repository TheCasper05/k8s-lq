"""Caso de uso para calificar conversaciones con rúbricas."""

import json
from datetime import datetime

from src.domain.models.message import Message
from src.domain.models.rubric import GradedMetric, Rubric, RubricGrade, RubricGradeMetadata
from src.domain.ports.ai.llm_port import LLMPort
from src.prompt_manager.manager import PromptManager


class GradeRubricUseCase:
    """Caso de uso: Calificar una conversación usando una rúbrica."""

    def __init__(
        self,
        llm: LLMPort,
        prompt_manager: PromptManager,
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar calificaciones
            prompt_manager: Gestor de prompts para obtener templates
        """
        self.llm = llm
        self.prompt_manager = prompt_manager

    async def execute(
        self,
        conversation: str,
        rubric: Rubric,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> tuple[RubricGrade, RubricGradeMetadata]:
        """
        Ejecuta el caso de uso: califica una conversación usando una rúbrica.

        Args:
            conversation: Texto de la conversación entre estudiante y asistente
            rubric: Rúbrica con las métricas a evaluar
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (RubricGrade con las calificaciones, RubricGradeMetadata con información de la generación)

        Raises:
            ValueError: Si la conversación o la rúbrica están vacías
            AIProviderError: Si hay un error al generar la calificación
        """
        # Validar inputs
        if not conversation or not conversation.strip():
            raise ValueError("La conversación no puede estar vacía")

        if not rubric.metrics:
            raise ValueError("La rúbrica debe contener al menos una métrica")

        # Obtener el prompt del sistema
        system_prompt = self.prompt_manager.render(
            "rubrics",
            "grading_system",
            version="v1",
        )

        # Convertir la rúbrica a formato JSON para el prompt
        metrics_json = json.dumps(
            [
                {
                    "name": metric.name,
                    "metric_description": metric.metric_description,
                    "grading_type": metric.grading_type,
                    "grading_type_description": metric.grading_type_description,
                }
                for metric in rubric.metrics
            ],
            ensure_ascii=False,
        )

        # Obtener el prompt del usuario
        user_prompt = self.prompt_manager.render(
            "rubrics",
            "grading_user",
            version="v1",
            conversation=conversation,
            metrics=str(metrics_json),
        )

        # Obtener el schema de respuesta
        response_schema = self.prompt_manager.render(
            "rubrics",
            "grading_response_schema",
            version="v1",
        )

        # Crear mensaje del usuario
        messages = []
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

        # Construir el objeto RubricGrade desde el dict
        graded_metrics = []
        for metric_data in result.get("metrics", []):
            graded_metric = GradedMetric(
                name=metric_data.get("name", ""),
                grade=metric_data.get("grade", ""),
                explanation=metric_data.get("explanation", ""),
            )
            graded_metrics.append(graded_metric)

        rubric_grade = RubricGrade(metrics=graded_metrics)

        # Extraer información de metadata del LLMResponse
        metadata = response.metadata or {}
        tokens_used = response.tokens_used or metadata.get("total_tokens")

        # Construir metadata
        rubric_grade_metadata = RubricGradeMetadata(
            provider=response.provider,
            model=response.model,
            tokens_used=tokens_used,
            finish_reason=response.finish_reason,
        )

        return rubric_grade, rubric_grade_metadata
