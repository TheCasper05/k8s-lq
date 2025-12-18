"""Modelos del dominio para escenarios de conversación."""

from dataclasses import dataclass


@dataclass
class Scenario:
    """Representa un escenario de conversación para práctica de idiomas."""

    title: str
    assistant_gender: str  # "male" | "female"
    scenario_type: str  # "teacher" | "roleplay" | "knowledge"
    practice_topic: str
    complete_description: str
    theme: str
    assistant_role: str
    user_role: str
    setting: str
    potential_directions: str
    example: str
    additional_data: list[str]
    appropriate: bool


@dataclass
class ScenarioMetadata:
    """Metadata de la generación del escenario."""

    provider: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
