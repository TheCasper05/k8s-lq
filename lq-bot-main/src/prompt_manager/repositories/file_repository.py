from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from src.prompt_manager.models import PromptDefinition, PromptKey
from src.prompt_manager.repositories.base import PromptRepository

SUPPORTED_EXTS = {".md", ".txt", ".json"}


class FilePromptRepository(PromptRepository):
    """
    Repositorio de solo-lectura que busca prompts en archivos .md/.txt/.json
    bajo una raíz con estructura versionada:

        prompts/
          conversations/
            v1/
              prompt_chat.md
            v2/
              prompt_chat.md
          scenarios/
            v1/
              create.txt

    Notas:
    - Carga on-demand: lee el archivo solo cuando se pide.
    - Puede bloquear el GIL si los archivos son grandes (aceptado en v1).
    - Los archivos .json se cargan como dict, .md/.txt como str.
    - Soporta versionado mediante subdirectorios v1, v2, etc.
    - Fallback: busca directamente en category/ si no encuentra en version/ (compatibilidad hacia atrás).
    """

    def __init__(self, root_dir: str | Path) -> None:
        self.root = Path(root_dir)

    def _file_for(self, category: str, name: str, version: str = "v1") -> Path | None:
        """
        Devuelve el path del archivo si existe para (category, version, name)
        probando las extensiones soportadas en SUPPORTED_EXTS.

        Busca en la estructura: category/version/name.ext
        """
        cat_dir = self.root / category
        if not cat_dir.is_dir():
            return None

        # Buscar en el subdirectorio de versión
        version_dir = cat_dir / version
        if version_dir.is_dir():
            for ext in SUPPORTED_EXTS:
                candidate = version_dir / f"{name}{ext}"
                if candidate.is_file():
                    return candidate

        # Fallback: buscar directamente en category (compatibilidad hacia atrás)
        for ext in SUPPORTED_EXTS:
            candidate = cat_dir / f"{name}{ext}"
            if candidate.is_file():
                return candidate
        return None

    # -------- API PromptRepository --------

    def get_prompt(self, category: str, name: str, version: str = "v1") -> PromptDefinition | None:
        file_path = self._file_for(category, name, version)
        if not file_path:
            return None

        # ⚠️ I/O on-demand; aceptado en v1 por ser repo secundario.
        if file_path.suffix == ".json":
            content = json.loads(file_path.read_text(encoding="utf-8"))
        else:
            content = file_path.read_text(encoding="utf-8")
        return PromptDefinition(key=PromptKey(category, name, version), content=content)

    def list_categories(self) -> Iterable[str]:
        if not self.root.exists():
            return []
        return [p.name for p in self.root.iterdir() if p.is_dir()]

    def list_prompts(self, category: str, version: str = "v1") -> Iterable[str]:
        cat_dir = self.root / category
        if not cat_dir.is_dir():
            return []
        names: list[str] = []

        # Buscar en el subdirectorio de versión
        version_dir = cat_dir / version
        if version_dir.is_dir():
            for p in version_dir.iterdir():
                if p.is_file() and p.suffix in SUPPORTED_EXTS:
                    names.append(p.stem)  # nombre sin extensión

        # Fallback: buscar directamente en category (compatibilidad hacia atrás)
        for p in cat_dir.iterdir():
            if p.is_file() and p.suffix in SUPPORTED_EXTS:
                names.append(p.stem)

        return names
