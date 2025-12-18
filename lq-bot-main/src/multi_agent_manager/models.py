from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from src.multi_agent_manager.exceptions import InvalidProcessDefinitionError


@dataclass(frozen=True, slots=True)
class PromptRef:
    """Referencia a un prompt en el catálogo de PromptManager."""

    category: str
    name: str
    version: str = "v1"

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> PromptRef:
        try:
            return cls(
                category=str(data["category"]),
                name=str(data["name"]),
                version=str(data.get("version", "v1")),
            )
        except KeyError as exc:
            raise InvalidProcessDefinitionError(
                "Prompt reference must include 'category' and 'name'."
            ) from exc


@dataclass(slots=True)
class AgentStepDefinition:
    """
    Describe un paso dentro de un proceso multi-agente.

    Cada step define qué prompts se usan y con qué contexto estático.
    El contexto compartido (previous_output, outputs previos, etc.)
    se inyecta en tiempo de ejecución.
    """

    id: str
    user_prompt: PromptRef
    system_prompt: PromptRef | None = None
    response_schema: PromptRef | None = None
    context: dict[str, Any] = field(default_factory=dict)
    llm_params: dict[str, Any] = field(default_factory=dict)
    output_key: str | None = None
    stop_on_error: bool = True

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AgentStepDefinition:
        if "id" not in data:
            raise InvalidProcessDefinitionError("Each step needs an 'id'.")
        if "user_prompt" not in data:
            raise InvalidProcessDefinitionError("Each step needs a 'user_prompt'.")

        user_prompt = data["user_prompt"]
        system_prompt = data.get("system_prompt")
        response_schema = data.get("response_schema")

        return cls(
            id=str(data["id"]),
            user_prompt=PromptRef.from_dict(user_prompt),
            system_prompt=PromptRef.from_dict(system_prompt) if system_prompt else None,
            response_schema=PromptRef.from_dict(response_schema) if response_schema else None,
            context=dict(data.get("context") or {}),
            llm_params=dict(data.get("llm_params") or {}),
            output_key=data.get("output_key"),
            stop_on_error=bool(data.get("stop_on_error", True)),
        )


@dataclass(slots=True)
class AgentProcessDefinition:
    """Un proceso multi-step definido como una lista de agentes/steps en orden."""

    name: str
    steps: list[AgentStepDefinition]

    @classmethod
    def from_raw(
        cls, raw: AgentProcessDefinition | Mapping[str, Any] | Iterable[Mapping[str, Any]]
    ) -> AgentProcessDefinition:
        if isinstance(raw, AgentProcessDefinition):
            return raw

        if isinstance(raw, Mapping):
            name = str(raw.get("name", "anonymous_process"))
            steps_raw = raw.get("steps")
            if not isinstance(steps_raw, Iterable):
                raise InvalidProcessDefinitionError(
                    "Process definition must contain a 'steps' array."
                )
            steps = [AgentStepDefinition.from_dict(item) for item in steps_raw]
            return cls(name=name, steps=steps)

        if isinstance(raw, Iterable) and not isinstance(raw, (str, bytes)):
            steps = [AgentStepDefinition.from_dict(item) for item in raw]
            return cls(name="anonymous_process", steps=steps)

        raise InvalidProcessDefinitionError("Unsupported process definition format.")


@dataclass(slots=True)
class AgentStepResult:
    """Resultado de la ejecución de un step."""

    step_id: str
    output_key: str
    llm_response: Any | None
    rendered_user_prompt: str | None
    rendered_system_prompt: str | None
    response_schema: dict[str, Any] | None
    error: Exception | None = None
