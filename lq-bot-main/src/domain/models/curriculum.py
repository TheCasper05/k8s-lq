"""Modelos del dominio para currículos educativos."""

from dataclasses import dataclass


@dataclass
class Submodule:
    """Representa un submódulo dentro de un currículo."""

    name: str
    scenarios: list[str]


@dataclass
class Curriculum:
    """Representa la estructura de un currículo educativo."""

    name: str
    description: str
    submodules: list[Submodule]


@dataclass
class CurriculumMetadata:
    """Metadata de la generación del currículo."""

    provider: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
