from abc import ABC, abstractmethod
from enum import IntEnum


class LogLevel(IntEnum):
    """Niveles de logging."""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LoggerPort(ABC):
    """Port para servicios de logging."""

    @abstractmethod
    def trace(self, message: str, **context) -> None:
        """Log nivel TRACE con contexto adicional."""
        pass

    @abstractmethod
    def debug(self, message: str, **context) -> None:
        """Log nivel DEBUG con contexto adicional."""
        pass

    @abstractmethod
    def info(self, message: str, **context) -> None:
        """Log nivel INFO con contexto adicional."""
        pass

    @abstractmethod
    def success(self, message: str, **context) -> None:
        """Log nivel SUCCESS con contexto adicional."""
        pass

    @abstractmethod
    def warning(self, message: str, **context) -> None:
        """Log nivel WARNING con contexto adicional."""
        pass

    @abstractmethod
    def error(self, message: str, exception: Exception | None = None, **context) -> None:
        """Log nivel ERROR con excepción y contexto."""
        pass

    @abstractmethod
    def critical(self, message: str, exception: Exception | None = None, **context) -> None:
        """Log nivel CRITICAL con excepción y contexto."""
        pass

    @abstractmethod
    def with_context(self, **context) -> "LoggerPort":
        """
        Retorna un logger con contexto adicional fijo.

        Ejemplo:
            logger = logger.with_context(user_id="123", session_id="abc")
            logger.info("Acción realizada")  # Incluye user_id y session_id
        """
        pass
