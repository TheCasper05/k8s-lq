"""Caso de uso para crear escenarios de conversación."""

import json
from datetime import datetime

from src.config import Settings
from src.domain.models.message import Message
from src.domain.models.scenario import Scenario, ScenarioMetadata
from src.domain.ports.ai.llm_port import LLMPort
from src.multi_agent_manager.manager import MultiAgentManager
from src.prompt_manager.manager import PromptManager


class CreateScenarioUseCase:
    """Caso de uso: Crear un escenario de conversación usando multi-agent o LLM directo."""

    def __init__(
        self,
        llm: LLMPort,
        prompt_manager: PromptManager,
        multi_agent_manager: MultiAgentManager | None = None,
        settings: Settings | None = None,
    ):
        """
        Inicializa el caso de uso con sus dependencias.

        Args:
            llm: Puerto LLM para generar escenarios
            prompt_manager: Gestor de prompts para obtener templates
            multi_agent_manager: Gestor multi-agente (opcional)
            settings: Configuración de la aplicación
        """
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.multi_agent_manager = multi_agent_manager
        self.settings = settings or Settings()

    async def execute(
        self,
        user_request: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> tuple[Scenario, ScenarioMetadata]:
        """
        Ejecuta el caso de uso: crea un escenario de conversación.

        Args:
            user_request: Solicitud del usuario para crear el escenario
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens a generar

        Returns:
            Tuple con (Scenario generado, ScenarioMetadata con información de la generación)

        Raises:
            AIProviderError: Si hay un error al generar el escenario
            ValueError: Si no se puede parsear la respuesta como JSON
        """
        if self.settings.scenario_multi_agent and self.multi_agent_manager:
            return await self._execute_multi_agent(user_request, temperature, max_tokens)
        else:
            return await self._execute_single_llm(user_request, temperature, max_tokens)

    async def _execute_multi_agent(
        self, user_request: str, temperature: float, max_tokens: int
    ) -> tuple[Scenario, ScenarioMetadata]:
        """Ejecuta usando el multi-agent manager."""
        results = await self.multi_agent_manager.execute_from_repo(
            category="scenarios",
            name="create_multi_agent_process",
            version="v1",
            initial_context={"user_request": user_request},
            llm_defaults={"temperature": temperature, "max_tokens": max_tokens},
        )

        # El último step contiene el escenario completo
        last_result = results[-1]
        if last_result.error:
            raise ValueError(f"Error en el proceso multi-agent: {last_result.error}")

        if not last_result.llm_response:
            raise ValueError("No se obtuvo respuesta del LLM en el proceso multi-agent")

        scenario_dict = self._parse_scenario_json(last_result.llm_response.content)
        scenario = self._dict_to_scenario(scenario_dict)

        # Metadata del último step - calcular tokens_used sumando todos los steps exitosos
        tokens_used = sum(
            result.llm_response.tokens_used or 0
            for result in results
            if result.llm_response is not None
        )

        scenario_metadata = ScenarioMetadata(
            provider=last_result.llm_response.provider,
            model=last_result.llm_response.model,
            tokens_used=tokens_used,
            finish_reason=last_result.llm_response.finish_reason,
        )

        return scenario, scenario_metadata

    async def _execute_single_llm(
        self, user_request: str, temperature: float, max_tokens: int
    ) -> tuple[Scenario, ScenarioMetadata]:
        """Ejecuta usando un solo llamado al LLM con el prompt directo."""
        # Obtener el prompt del sistema
        system_prompt = self.prompt_manager.render(
            "scenarios",
            "create_system",
            version="v1",
        )

        # Obtener el prompt del usuario
        user_prompt = self.prompt_manager.render(
            "scenarios",
            "create_user",
            version="v1",
            context=user_request,
            language="English",  # Por ahora hardcodeado, después se ajustará
        )

        # Obtener el schema de respuesta
        response_schema = self.prompt_manager.render(
            "scenarios",
            "create_response_schema",
            version="v1",
        )

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

        scenario_dict = self._parse_scenario_json(response.content)
        scenario = self._dict_to_scenario(scenario_dict)

        # Metadata
        metadata = response.metadata or {}
        tokens_used = response.tokens_used or metadata.get("total_tokens")

        scenario_metadata = ScenarioMetadata(
            provider=response.provider,
            model=response.model,
            tokens_used=tokens_used,
            finish_reason=response.finish_reason,
        )

        return scenario, scenario_metadata

    def _parse_scenario_json(self, content: str) -> dict:
        """Parsea el contenido JSON del escenario."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as err:
            # Intentar extraer JSON del contenido si está envuelto
            content = content.strip()
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                try:
                    return json.loads(content[start_idx:end_idx])
                except json.JSONDecodeError:
                    raise ValueError(
                        f"No se pudo parsear la respuesta como JSON: {content}"
                    ) from err
            else:
                raise ValueError(f"No se pudo parsear la respuesta como JSON: {content}") from err

    def _dict_to_scenario(self, data: dict) -> Scenario:
        """Convierte un diccionario a un objeto Scenario."""
        return Scenario(
            title=data.get("title", ""),
            assistant_gender=data.get("assistant_gender", "male"),
            scenario_type=data.get("scenario_type", "roleplay"),
            practice_topic=data.get("practice_topic", "all"),
            complete_description=data.get("complete_description", ""),
            theme=data.get("theme", ""),
            assistant_role=data.get("assistant_role", ""),
            user_role=data.get("user_role", ""),
            setting=data.get("setting", ""),
            potential_directions=data.get("potential_directions", ""),
            example=data.get("example", ""),
            additional_data=data.get("additional_data", []),
            appropriate=data.get("appropriate", True),
        )
