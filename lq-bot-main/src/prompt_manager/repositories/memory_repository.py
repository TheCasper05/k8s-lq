from __future__ import annotations

from collections.abc import Iterable, Mapping

from src.prompt_manager.models import PromptDefinition, PromptKey
from src.prompt_manager.repositories.base import PromptRepository


class InMemoryPromptRepository(PromptRepository):
    """
    Repositorio principal (rápido, libre de I/O) basado en estructuras en memoria.

    Estructura esperada (con versionado):
        {
          "corrections": {
            "v1": {
              "grammar": "Corrige esto en {idioma}:\n{texto}",
            },
            "v2": {
              "grammar": "Nueva versión del prompt...",
            }
          },
          "scenarios": {
            "v1": {
              "create": "Hola {username}, escribe sobre {topic}",
            }
          },
          "schemas": {
            "v1": {
              "response_schema": {"type": "object", "properties": {...}},
            }
          }
        }

    Notas:
    - Lecturas son O(1) promedio.
    - Mutaciones (register / bulk_register) son opcionales y útiles en dev/tests.
    - El contenido puede ser str (template) o dict (esquema estructurado).
    - Soporta versionado mediante estructura anidada: category -> version -> name.
    """

    def __init__(
        self, prompts: Mapping[str, Mapping[str, Mapping[str, str | dict]]] | None = None
    ) -> None:
        # Copia defensiva a dicts mutables internos
        # Estructura: {category: {version: {name: content}}}
        self._prompts: dict[str, dict[str, dict[str, str | dict]]] = {}
        if prompts:
            for cat, versions in prompts.items():
                self._prompts[cat] = {}
                for version, items in versions.items():
                    self._prompts[cat][version] = dict(items)

    # -------- API PromptRepository --------

    def get_prompt(self, category: str, name: str, version: str = "v1") -> PromptDefinition | None:
        content = self._prompts.get(category, {}).get(version, {}).get(name)
        if content is None:
            return None
        return PromptDefinition(key=PromptKey(category, name, version), content=content)

    def list_categories(self) -> Iterable[str]:
        # Devolvemos una lista para materializar el snapshot actual
        return list(self._prompts.keys())

    def list_prompts(self, category: str, version: str = "v1") -> Iterable[str]:
        return list(self._prompts.get(category, {}).get(version, {}).keys())

    # -------- Utilidades opcionales (útiles en dev/tests) --------

    def register(self, category: str, name: str, content: str | dict, version: str = "v1") -> None:
        """
        Registra o sobrescribe un prompt individual en memoria.
        El contenido puede ser str (template) o dict (esquema estructurado).
        """
        self._prompts.setdefault(category, {}).setdefault(version, {})[name] = content

    def bulk_register(self, prompts: Mapping[str, Mapping[str, Mapping[str, str | dict]]]) -> None:
        """
        Registra múltiples prompts por categoría y versión.
        El contenido puede ser str (template) o dict (esquema estructurado).
        Estructura esperada: {category: {version: {name: content}}}
        """
        for cat, versions in prompts.items():
            cat_bucket = self._prompts.setdefault(cat, {})
            for ver, items in versions.items():
                ver_bucket = cat_bucket.setdefault(ver, {})
                ver_bucket.update(items)

    def has_prompt(self, category: str, name: str, version: str = "v1") -> bool:
        return name in self._prompts.get(category, {}).get(version, {})
