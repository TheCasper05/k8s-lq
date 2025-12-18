from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from src.prompt_manager.models import PromptDefinition


class PromptRepository(Protocol):
    """
    Contrato mínimo para cualquier repositorio de prompts.
    """

    def get_prompt(self, category: str, name: str, version: str = "v1") -> PromptDefinition | None:
        """
        Devuelve la definición del prompt o None si no existe.
        """
        ...

    def list_categories(self) -> Iterable[str]:
        """
        Devuelve un iterable con los nombres de categorías disponibles.
        """
        ...

    def list_prompts(self, category: str, version: str = "v1") -> Iterable[str]:
        """
        Devuelve un iterable con los nombres de prompts dentro de la categoría y versión.
        """
        ...
