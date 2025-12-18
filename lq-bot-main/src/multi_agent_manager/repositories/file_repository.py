from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from src.multi_agent_manager.models import AgentProcessDefinition
from src.multi_agent_manager.repositories.base import ProcessRepository

SUPPORTED_EXTS = {".json"}


class FileProcessRepository(ProcessRepository):
    """
    Repositorio de solo-lectura para procesos multi-agente definidos en archivos JSON.

    Estructura esperada (análoga a prompts):
        prompts/
          scenarios/
            v1/
              create_multi_agent_process.json
    """

    def __init__(self, root_dir: str | Path) -> None:
        self.root = Path(root_dir)

    def _file_for(self, category: str, name: str, version: str = "v1") -> Path | None:
        cat_dir = self.root / category
        if not cat_dir.is_dir():
            return None

        version_dir = cat_dir / version
        if version_dir.is_dir():
            candidate = version_dir / f"{name}.json"
            if candidate.is_file():
                return candidate

        # Fallback sin versión (compatibilidad)
        candidate = cat_dir / f"{name}.json"
        if candidate.is_file():
            return candidate
        return None

    # -------- API ProcessRepository --------
    def get_process(
        self, category: str, name: str, version: str = "v1"
    ) -> AgentProcessDefinition | None:
        file_path = self._file_for(category, name, version)
        if not file_path:
            return None

        content = json.loads(file_path.read_text(encoding="utf-8"))
        return AgentProcessDefinition.from_raw(content)

    def list_categories(self) -> Iterable[str]:
        if not self.root.exists():
            return []
        return [p.name for p in self.root.iterdir() if p.is_dir()]

    def list_processes(self, category: str, version: str = "v1") -> Iterable[str]:
        cat_dir = self.root / category
        if not cat_dir.is_dir():
            return []
        names: list[str] = []

        version_dir = cat_dir / version
        if version_dir.is_dir():
            for p in version_dir.iterdir():
                if p.is_file() and p.suffix in SUPPORTED_EXTS:
                    names.append(p.stem)

        for p in cat_dir.iterdir():
            if p.is_file() and p.suffix in SUPPORTED_EXTS:
                names.append(p.stem)

        return names
