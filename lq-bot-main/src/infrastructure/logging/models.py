from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class LogEntry:
    """Entrada de log estructurada."""

    # Campos estándar
    timestamp: datetime
    level: str
    message: str
    logger_name: str

    # Contexto de trazabilidad
    correlation_id: str
    request_id: str | None = None
    user_id: str | None = None
    session_id: str | None = None

    # Contexto técnico
    service: str = "lingobot"
    environment: str = "local"
    version: str = "0.1.0"
    hostname: str = ""

    # Contexto de ubicación en código
    module: str | None = None
    function: str | None = None
    line_number: int | None = None

    # Excepción (si aplica)
    exception_type: str | None = None
    exception_message: str | None = None
    stack_trace: str | None = None

    # Métricas de performance
    duration_ms: float | None = None
    tokens_used: int | None = None
    cost_usd: float | None = None

    # Contexto del proveedor AI
    ai_provider: str | None = None
    ai_model: str | None = None
    ai_operation: str | None = None

    # Contexto de negocio
    endpoint: str | None = None
    http_method: str | None = None
    status_code: int | None = None
    user_agent: str | None = None
    ip_address: str | None = None

    # Datos adicionales (flexible)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para JSON."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        # Remover campos None para reducir tamaño
        return {k: v for k, v in data.items() if v is not None}

    def to_json(self) -> str:
        """Convierte a JSON string."""
        import json

        return json.dumps(self.to_dict())


@dataclass
class LogSpan:
    """Representa un span de operación para tracking."""

    operation: str
    correlation_id: str
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    duration_ms: float | None = None
    status: str = "running"  # running | success | error
    context: dict[str, Any] = field(default_factory=dict)

    def __enter__(self):
        """Context manager enter."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - calcula duración."""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000

        if exc_type is None:
            self.status = "success"
        else:
            self.status = "error"
            self.context["exception"] = str(exc_val)

        return False  # No suprimir excepciones
