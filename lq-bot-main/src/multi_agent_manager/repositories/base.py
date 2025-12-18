from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from src.multi_agent_manager.models import AgentProcessDefinition


class ProcessRepository(Protocol):
    """Contrato mínimo para repositorios de procesos multi-agente."""

    def get_process(
        self, category: str, name: str, version: str = "v1"
    ) -> AgentProcessDefinition | None:
        """Devuelve la definición del proceso o None si no existe."""
        ...

    def list_categories(self) -> Iterable[str]:
        """Devuelve un iterable con los nombres de categorías disponibles."""
        ...

    def list_processes(self, category: str, version: str = "v1") -> Iterable[str]:
        """Devuelve los nombres de procesos dentro de la categoría y versión."""
        ...
