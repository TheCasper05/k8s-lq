from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from src.domain.models.message import Message
from src.domain.ports.ai.llm_port import LLMPort
from src.multi_agent_manager.exceptions import (
    InvalidProcessDefinitionError,
    PromptRenderingError,
    StepExecutionError,
)
from src.multi_agent_manager.models import (
    AgentProcessDefinition,
    AgentStepDefinition,
    AgentStepResult,
    PromptRef,
)
from src.multi_agent_manager.repositories import ProcessRepository
from src.prompt_manager.manager import PromptManager


class MultiAgentManager:
    """
    Orquestador de procesos multi-paso basados en prompts manejados por PromptManager.

    - Cada proceso se define como un array JSON de steps (agent definitions).
    - Cada step puede declarar prompts de sistema/usuario y un response_schema opcional.
    - El output de cada step se inyecta en el contexto del siguiente como `previous_output`
      y también bajo la clave `output_key` definida en el step (default: id del step).
    """

    def __init__(
        self,
        prompt_manager: PromptManager,
        llm: LLMPort,
        process_repository: ProcessRepository | None = None,
    ):
        self._prompt_manager = prompt_manager
        self._llm = llm
        self._process_repo = process_repository

    async def execute(
        self,
        process_definition: AgentProcessDefinition | dict[str, Any] | list[dict[str, Any]],
        initial_context: dict[str, Any] | None = None,
        llm_defaults: dict[str, Any] | None = None,
    ) -> list[AgentStepResult]:
        """
        Ejecuta un proceso multi-step.

        Args:
            process_definition: AgentProcessDefinition o estructura cruda (dict/list) decodificada de JSON.
            initial_context: Variables iniciales disponibles para renderizar prompts.
            llm_defaults: Parámetros default para el LLM (temperatura, max_tokens, etc.).

        Returns:
            Lista de resultados por step en orden de ejecución.
        """
        process = AgentProcessDefinition.from_raw(process_definition)
        shared_context: dict[str, Any] = dict(initial_context or {})
        results: list[AgentStepResult] = []
        previous_output: str | None = shared_context.get("previous_output")
        defaults = dict(llm_defaults or {})

        for step in process.steps:
            render_context = self._build_context(shared_context, step, previous_output)

            try:
                system_prompt = (
                    self._render_prompt(step.id, "system", step.system_prompt, render_context)
                    if step.system_prompt
                    else None
                )
                user_prompt = self._render_prompt(step.id, "user", step.user_prompt, render_context)
                response_schema = (
                    self._render_prompt(
                        step.id, "response_schema", step.response_schema, render_context
                    )
                    if step.response_schema
                    else None
                )
            except Exception as exc:  # PromptManager lanza sus propias excepciones
                raise PromptRenderingError(step.id, "prompt", exc) from exc

            if user_prompt is None:
                raise InvalidProcessDefinitionError(
                    f"Step '{step.id}' produced an empty user prompt."
                )
            if step.system_prompt and system_prompt is None:
                raise InvalidProcessDefinitionError(
                    f"Step '{step.id}' produced an empty system prompt."
                )

            llm_kwargs = self._build_llm_kwargs(defaults, step.llm_params, response_schema)
            message = Message(
                role="user", content=user_prompt, timestamp=datetime.now(), metadata=None
            )

            try:
                llm_response = await self._llm.generate_response(
                    messages=[message],
                    system_prompt=system_prompt,
                    **llm_kwargs,
                )
            except Exception as exc:
                if step.stop_on_error:
                    raise StepExecutionError(process.name, step.id, exc) from exc
                llm_response = None
                step_error: Exception | None = exc
            else:
                step_error = None

            output_key = step.output_key or step.id
            if llm_response:
                previous_output = llm_response.content
                shared_context["previous_output"] = previous_output
                shared_context[output_key] = llm_response.content

                # Si el output es JSON parseable a dict, lo fusionamos en el contexto.
                try:
                    parsed = json.loads(llm_response.content)
                    if isinstance(parsed, dict):
                        shared_context.update(parsed)
                        shared_context["outputs"] = shared_context.get("outputs", {})
                        shared_context["outputs"].update(parsed)
                except Exception:
                    pass
            else:
                previous_output = None
                shared_context[output_key] = None

            results.append(
                AgentStepResult(
                    step_id=step.id,
                    output_key=output_key,
                    llm_response=llm_response,
                    rendered_user_prompt=user_prompt,
                    rendered_system_prompt=system_prompt,
                    response_schema=response_schema if isinstance(response_schema, dict) else None,
                    error=step_error,
                )
            )

        return results

    async def execute_from_repo(
        self,
        category: str,
        name: str,
        version: str = "v1",
        initial_context: dict[str, Any] | None = None,
        llm_defaults: dict[str, Any] | None = None,
    ) -> list[AgentStepResult]:
        """
        Carga el proceso desde el repositorio (si está configurado) y lo ejecuta.
        """
        if self._process_repo is None:
            raise InvalidProcessDefinitionError(
                "No process repository configured in MultiAgentManager."
            )

        process = self._process_repo.get_process(category, name, version)
        if process is None:
            raise InvalidProcessDefinitionError(
                f"Process not found: category='{category}', version='{version}', name='{name}'"
            )

        return await self.execute(
            process, initial_context=initial_context, llm_defaults=llm_defaults
        )

    def _build_context(
        self, shared_context: dict[str, Any], step: AgentStepDefinition, previous_output: str | None
    ) -> dict[str, Any]:
        ctx = dict(shared_context)
        ctx.update(step.context)
        if previous_output is not None:
            ctx.setdefault("previous_output", previous_output)
            ctx.setdefault("last_output", previous_output)
        # Facilitar acceso a outputs anteriores por id
        ctx.setdefault("outputs", {})
        for key, value in shared_context.items():
            if key not in ("previous_output", "outputs") and key not in step.context:
                ctx["outputs"][key] = value
        return ctx

    def _render_prompt(
        self, step_id: str, prompt_type: str, prompt_ref: PromptRef | None, context: dict[str, Any]
    ) -> str | dict | None:
        if prompt_ref is None:
            return None
        rendered = self._prompt_manager.render(
            prompt_ref.category,
            prompt_ref.name,
            version=prompt_ref.version,
            **context,
        )

        # Validaciones rápidas para tipos esperados
        if prompt_type in {"user", "system"} and isinstance(rendered, dict):
            raise InvalidProcessDefinitionError(
                f"Step '{step_id}' {prompt_type} prompt returned a dict, expected string."
            )
        if (
            prompt_type == "response_schema"
            and rendered is not None
            and not isinstance(rendered, dict)
        ):
            try:
                parsed = json.loads(rendered)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            raise InvalidProcessDefinitionError(
                f"Step '{step_id}' response_schema must render to dict or JSON string."
            )

        return rendered

    def _build_llm_kwargs(
        self,
        defaults: dict[str, Any],
        step_params: dict[str, Any],
        response_schema: str | dict | None,
    ) -> dict[str, Any]:
        kwargs = dict(defaults)
        kwargs.update(step_params or {})
        if isinstance(response_schema, dict):
            kwargs.setdefault("json_schema", response_schema)
        return kwargs
