from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal


@dataclass
class Message:
    """Representa un mensaje en una conversación."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class LLMResponse:
    """Respuesta de un modelo de lenguaje."""

    content: str
    provider: str
    model: str
    tokens_used: int
    finish_reason: str | None = None
    incomplete_reason: str | None = None
    response_id: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
