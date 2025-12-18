"""Caso de uso para crear rúbricas de evaluación."""

import json
import mimetypes
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from src.domain.models.message import Message
from src.domain.models.rubric import Metric, Rubric, RubricMetadata
from src.domain.ports.ai.llm_port import LLMPort
from src.domain.ports.storage.file_storage_port import FileStoragePort
from src.prompt_manager.manager import PromptManager


class CreateRubricUseCase:
    """Caso de uso: Crear una rúbrica de evaluación de conversaciones."""

    def __init__(
        self,
        llm: LLMPort,
        prompt_manager: PromptManager,
        storage: FileStoragePort | None = None,
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar rúbricas
            prompt_manager: Gestor de prompts para obtener templates
            storage: Puerto de almacenamiento para leer archivos (opcional)
        """
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.storage = storage

    async def execute(
        self,
        text: str | None = None,
        file_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> tuple[Rubric, RubricMetadata]:
        """
        Ejecuta el caso de uso: crea una rúbrica de evaluación.

        Args:
            text: Explicación opcional del profesor sobre las métricas de evaluación
            file_url: URL opcional del archivo que contiene información adicional
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (Rubric generada, RubricMetadata con información de la generación)

        Raises:
            ValueError: Si file_url se proporciona pero el archivo no existe, o si ni text ni file_url están presentes
            AIProviderError: Si hay un error al generar la rúbrica
        """
        # Validar que al menos uno de los campos esté presente
        if not text and not file_url:
            raise ValueError("Debe proporcionarse al menos uno de los campos: 'text' o 'file_url'")

        # Preparar archivos si hay file_url
        files_list: list[tuple[str, bytes, str]] | None = None
        if file_url is not None:
            # Validar que el archivo existe
            parsed = urlparse(file_url)
            key = parsed.path.lstrip("/")
            if self.storage is None:
                raise ValueError("Storage adapter no disponible para leer archivos")
            if not await self.storage.file_exists(key):
                raise ValueError(f"Archivo con URL '{file_url}' no encontrado")

            # Leer el archivo
            file_data = await self.storage.get_file(key)

            # Extraer nombre de archivo de la URL
            filename = Path(parsed.path).name or "file"

            # Detectar MIME type basado en la extensión
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                # Fallback a application/octet-stream si no se puede detectar
                mime_type = "application/octet-stream"

            files_list = [(filename, file_data, mime_type)]

        # Determinar qué prompts usar según si hay archivo o no
        if file_url is not None:
            # Obtener el prompt del sistema desde archivo
            system_prompt = self.prompt_manager.render(
                "rubrics",
                "creation_system_file",
                version="v1",
            )

            # Obtener el prompt del usuario con archivo
            # Si text es None, usar string vacío para el prompt
            text_value = text or ""
            user_prompt = self.prompt_manager.render(
                "rubrics",
                "creation_user_file",
                version="v1",
                text=text_value,
                file_id="",  # Ya no se usa file_id, se envía el archivo directamente
            )
        else:
            # Obtener el prompt del sistema desde archivo
            system_prompt = self.prompt_manager.render(
                "rubrics",
                "creation_system",
                version="v1",
            )

            # Obtener el prompt del usuario sin archivo
            # text no puede ser None aquí porque ya validamos que al menos uno esté presente
            user_prompt = self.prompt_manager.render(
                "rubrics",
                "creation_user",
                version="v1",
                text=text or "",
            )

        # Obtener el schema de respuesta (es un dict, no se renderiza)
        response_schema = self.prompt_manager.render(
            "rubrics",
            "creation_response_schema",
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
            files=files_list,
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

        # Construir el objeto Rubric desde el dict
        metrics = []
        for metric_data in result.get("metrics", []):
            metric = Metric(
                name=metric_data.get("name", ""),
                metric_description=metric_data.get("metric_description", ""),
                grading_type=metric_data.get("grading_type", "percentage"),
                grading_type_description=metric_data.get("grading_type_description", ""),
            )
            metrics.append(metric)

        rubric = Rubric(metrics=metrics)

        # Extraer información de metadata del LLMResponse
        metadata = response.metadata or {}
        tokens_used = response.tokens_used or metadata.get("total_tokens")

        # Construir metadata
        rubric_metadata = RubricMetadata(
            provider=response.provider,
            model=response.model,
            tokens_used=tokens_used,
            finish_reason=response.finish_reason,
        )

        return rubric, rubric_metadata
