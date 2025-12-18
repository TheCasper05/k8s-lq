"""Excepciones relacionadas con proveedores de IA."""

from typing import Any


class AIProviderError(Exception):
    """Excepción base para errores de proveedores de IA."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        original_error: Exception | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Inicializa la excepción.

        Args:
            message: Mensaje de error
            provider: Nombre del proveedor (openai, anthropic, etc.)
            original_error: Excepción original si existe
            metadata: Metadata adicional
        """
        self.message = message
        self.provider = provider
        self.original_error = original_error
        self.metadata = metadata or {}

        super().__init__(self.message)

    def __str__(self) -> str:
        """Representación en string del error."""
        base = self.message
        if self.provider:
            base = f"[{self.provider}] {base}"
        return base
