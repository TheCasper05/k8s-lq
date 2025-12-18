"""Modelos del dominio para rúbricas de evaluación."""

from dataclasses import dataclass


@dataclass
class Metric:
    """Representa una métrica individual de evaluación."""

    name: str
    metric_description: str
    grading_type: str
    grading_type_description: str


@dataclass
class Rubric:
    """Representa una rúbrica de evaluación de conversaciones."""

    metrics: list[Metric]


@dataclass
class RubricMetadata:
    """Metadata de la generación de la rúbrica."""

    provider: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None


@dataclass
class GradedMetric:
    """Representa una métrica calificada de una conversación."""

    name: str
    grade: str
    explanation: str


@dataclass
class RubricGrade:
    """Representa la calificación de una conversación usando una rúbrica."""

    metrics: list[GradedMetric]


@dataclass
class RubricGradeMetadata:
    """Metadata de la calificación de la rúbrica."""

    provider: str
    model: str
    tokens_used: int | None = None
    finish_reason: str | None = None
