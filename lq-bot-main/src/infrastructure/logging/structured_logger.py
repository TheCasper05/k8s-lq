import json
import logging
import socket
import sys
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

from src.domain.ports.logging.logger_port import LoggerPort, LogLevel
from src.infrastructure.logging.models import LogEntry, LogSpan

# ContextVar para correlation ID (thread-safe en async)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class StructuredLogger(LoggerPort):
    """Implementación de logger estructurado con JSON."""

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        output_file: Path | None = None,
        enable_console: bool = True,
        environment: str = "local",
        version: str = "0.1.0",
    ):
        self.name = name
        self.level = level
        self.environment = environment
        self.version = version
        self.hostname = socket.gethostname()

        # Contexto fijo del logger
        self.fixed_context: dict[str, Any] = {}

        # Configurar handlers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []  # Limpiar handlers existentes

        # Handler de consola (human-readable)
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_formatter = ColoredFormatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # Handler de archivo JSON
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(output_file)
            file_handler.setLevel(level)
            file_formatter = JSONFormatter()
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def trace(self, message: str, **context) -> None:
        self._log(LogLevel.TRACE, message, **context)

    def debug(self, message: str, **context) -> None:
        self._log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context) -> None:
        self._log(LogLevel.INFO, message, **context)

    def success(self, message: str, **context) -> None:
        self._log(LogLevel.SUCCESS, message, **context)

    def warning(self, message: str, **context) -> None:
        self._log(LogLevel.WARNING, message, **context)

    def error(self, message: str, exception: Exception | None = None, **context) -> None:
        if exception:
            context["exception_type"] = type(exception).__name__
            context["exception_message"] = str(exception)
            import traceback

            context["stack_trace"] = traceback.format_exc()

        self._log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, exception: Exception | None = None, **context) -> None:
        if exception:
            context["exception_type"] = type(exception).__name__
            context["exception_message"] = str(exception)
            import traceback

            context["stack_trace"] = traceback.format_exc()

        self._log(LogLevel.CRITICAL, message, **context)

    def with_context(self, **context) -> "StructuredLogger":
        """Crea un nuevo logger con contexto adicional fijo."""
        new_logger = StructuredLogger(
            name=self.name, level=self.level, environment=self.environment, version=self.version
        )
        new_logger.fixed_context = {**self.fixed_context, **context}
        new_logger.logger = self.logger  # Reusar mismo logger interno
        return new_logger

    def start_span(self, operation: str, **context) -> LogSpan:
        """Inicia un span para tracking."""
        correlation_id = self._get_correlation_id()
        span = LogSpan(operation=operation, correlation_id=correlation_id, context=context)

        # Log de inicio
        self.debug(f"Starting operation: {operation}", operation=operation, **context)

        return LogSpanContext(span, self)

    def _log(self, level: LogLevel, message: str, **context) -> None:
        """Método interno para crear y emitir log estructurado."""
        # Crear entrada de log
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level.name,
            message=message,
            logger_name=self.name,
            correlation_id=self._get_correlation_id(),
            service="lingobot",
            environment=self.environment,
            version=self.version,
            hostname=self.hostname,
            **self.fixed_context,
            **context,
        )

        # Agregar información de ubicación en código
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller_frame = frame.f_back.f_back
            entry.module = caller_frame.f_globals.get("__name__")
            entry.function = caller_frame.f_code.co_name
            entry.line_number = caller_frame.f_lineno

        # Emitir log
        log_dict = entry.to_dict()
        self.logger.log(level, message, extra={"log_entry": log_dict})

    def _get_correlation_id(self) -> str:
        """Obtiene correlation ID del contexto."""
        try:
            cid = correlation_id_var.get()
            if not cid:
                import uuid

                cid = str(uuid.uuid4())
                correlation_id_var.set(cid)
            return cid
        except Exception:
            import uuid

            return str(uuid.uuid4())


class LogSpanContext:
    """Context manager para LogSpan."""

    def __init__(self, span: LogSpan, logger: StructuredLogger):
        self.span = span
        self.logger = logger

    def __enter__(self):
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.span.__exit__(exc_type, exc_val, exc_tb)

        # Log de finalización
        if self.span.status == "success":
            self.logger.success(
                f"Completed operation: {self.span.operation}",
                operation=self.span.operation,
                duration_ms=self.span.duration_ms,
                **self.span.context,
            )
        else:
            self.logger.error(
                f"Failed operation: {self.span.operation}",
                operation=self.span.operation,
                duration_ms=self.span.duration_ms,
                **self.span.context,
            )

        return False


class JSONFormatter(logging.Formatter):
    """Formatter para logs en formato JSON."""

    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "log_entry"):
            return json.dumps(record.log_entry)
        else:
            # Fallback a formato simple
            return json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "logger": record.name,
                }
            )


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola."""

    COLORS = {
        "TRACE": "\033[36m",  # Cyan
        "DEBUG": "\033[34m",  # Blue
        "INFO": "\033[32m",  # Green
        "SUCCESS": "\033[92m",  # Bright Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[91m",  # Bright Red
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Agregar correlation_id al record si no existe
        if not hasattr(record, "correlation_id"):
            record.correlation_id = correlation_id_var.get("")[:8]

        # Colorizar nivel
        levelname = record.levelname
        color = self.COLORS.get(levelname, "")
        reset = self.COLORS["RESET"]
        record.levelname = f"{color}{levelname}{reset}"

        return super().format(record)
