from __future__ import annotations

from collections.abc import Callable

from src.prompt_manager.exceptions import PromptNotFoundError
from src.prompt_manager.models import PromptDefinition
from src.prompt_manager.repositories.base import PromptRepository
from src.prompt_manager.templates.engine import TemplateEngine

# Hooks
PreProcessor = Callable[[PromptDefinition], PromptDefinition]
PostProcessor = Callable[[str], str]  # Solo se aplica a strings renderizados


class PromptManager:
    """
    Orquesta repositorios y template engine.
    Orden de búsqueda por diseño v1: memory_repo -> file_repo (si existe).
    """

    def __init__(
        self,
        memory_repo: PromptRepository,
        template_engine: TemplateEngine | None = None,
        file_repo: PromptRepository | None = None,
    ) -> None:
        self._memory_repo = memory_repo
        self._file_repo = file_repo
        self._engine = template_engine or TemplateEngine()
        self._preprocessors: list[PreProcessor] = []
        self._postprocessors: list[PostProcessor] = []

    # ---------- Registro de hooks ----------
    def register_preprocessor(self, func: PreProcessor) -> None:
        """Se ejecutan sobre PromptDefinition ANTES de render."""
        self._preprocessors.append(func)

    def register_postprocessor(self, func: PostProcessor) -> None:
        """Se ejecutan sobre el string renderizado DESPUÉS de render."""
        self._postprocessors.append(func)

    # ---------- API principal ----------
    def get(self, category: str, name: str, version: str = "v1") -> PromptDefinition:
        """
        Obtiene un PromptDefinition aplicando preprocessors.
        Busca primero en memoria y luego en files (si hay file_repo).
        """
        pr = self._memory_repo.get_prompt(category, name, version)
        if pr is None and self._file_repo is not None:
            pr = self._file_repo.get_prompt(category, name, version)
        if pr is None:
            raise PromptNotFoundError(category, name, version)

        for pre in self._preprocessors:
            pr = pre(pr)
        return pr

    def render(self, category: str, name: str, version: str = "v1", **kwargs: object) -> str | dict:
        """
        Render del prompt (valida variables requeridas). Aplica postprocessors.
        Si el contenido es un dict (esquema estructurado), lo devuelve sin renderizar.
        """
        pr = self.get(category, name, version)
        if isinstance(pr.content, dict):
            # Los dicts (esquemas) no se renderizan, se devuelven directamente
            return pr.content
        rendered = self._engine.render(pr.content, **kwargs)
        for post in self._postprocessors:
            rendered = post(rendered)
        return rendered

    def list_categories(self) -> list[str]:
        """
        Unión ordenada de categorías de memory y file (si existe).
        """
        cats = set(self._memory_repo.list_categories())
        if self._file_repo is not None:
            cats.update(self._file_repo.list_categories())
        return sorted(cats)

    def list_prompts(self, category: str, version: str = "v1") -> list[str]:
        """
        Unión ordenada de nombres de prompt dentro de una categoría y versión.
        """
        names = set(self._memory_repo.list_prompts(category, version))
        if self._file_repo is not None:
            names.update(self._file_repo.list_prompts(category, version))
        return sorted(names)
