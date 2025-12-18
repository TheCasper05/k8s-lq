from pathlib import Path

from .exceptions import (
    InvalidPromptFormatError,
    MissingTemplateVariablesError,
    PromptManagerError,
    PromptNotFoundError,
)
from .manager import PostProcessor, PreProcessor, PromptManager
from .models import PromptDefinition, PromptKey, TenantContext
from .repositories import FilePromptRepository, InMemoryPromptRepository, PromptRepository
from .templates import Jinja2TemplateEngine, TemplateEngine

__all__ = [
    "FilePromptRepository",
    "InMemoryPromptRepository",
    "InvalidPromptFormatError",
    "Jinja2TemplateEngine",
    "MissingTemplateVariablesError",
    "PostProcessor",
    "PreProcessor",
    "PromptDefinition",
    "PromptKey",
    "PromptManager",
    "PromptManagerError",
    "PromptNotFoundError",
    "PromptRepository",
    "TemplateEngine",
    "TenantContext",
]


def _load_file_content(file_path: Path) -> str | dict:
    """
    Carga el contenido de un archivo.

    Args:
        file_path: Ruta del archivo

    Returns:
        Contenido del archivo (string o dict si es JSON)
    """
    import json

    if file_path.suffix == ".json":
        return json.loads(file_path.read_text(encoding="utf-8"))
    return file_path.read_text(encoding="utf-8")


def _process_version_directory(
    version_dir: Path, category: str, mem: InMemoryPromptRepository
) -> None:
    """
    Procesa un directorio de versión y registra sus archivos.

    Args:
        version_dir: Directorio de versión
        category: Categoría del prompt
        mem: Repositorio en memoria
    """
    version = version_dir.name
    for file_path in version_dir.iterdir():
        if file_path.is_file() and file_path.suffix in {".md", ".txt", ".json"}:
            content = _load_file_content(file_path)
            mem.register(category, file_path.stem, content, version)


def _process_legacy_directory(cat_dir: Path, category: str, mem: InMemoryPromptRepository) -> None:
    """
    Procesa un directorio en estructura antigua (sin versiones).

    Args:
        cat_dir: Directorio de categoría
        category: Categoría del prompt
        mem: Repositorio en memoria
    """
    for file_path in cat_dir.iterdir():
        if file_path.is_file() and file_path.suffix in {".md", ".txt", ".json"}:
            content = _load_file_content(file_path)
            mem.register(category, file_path.stem, content, "v1")


def preload_files_into_memory(files: FilePromptRepository, mem: InMemoryPromptRepository) -> None:
    """
    Precarga archivos de prompts desde el sistema de archivos a memoria.

    Args:
        files: Repositorio de archivos
        mem: Repositorio en memoria
    """
    import re

    root: Path = files.root
    if not root.exists():
        return

    # Patrón para detectar versiones: v1, v2, v10, etc.
    version_pattern = re.compile(r"^v\d+$")

    for cat_dir in root.iterdir():
        if not cat_dir.is_dir():
            continue

        category = cat_dir.name

        # Verificar si hay subdirectorios de versión
        version_dirs = [
            d for d in cat_dir.iterdir() if d.is_dir() and version_pattern.match(d.name)
        ]

        if version_dirs:
            # Estructura nueva: category/version/file.ext
            for version_dir in version_dirs:
                _process_version_directory(version_dir, category, mem)
        else:
            # Estructura antigua (compatibilidad hacia atrás): category/file.ext -> se registra como v1
            _process_legacy_directory(cat_dir, category, mem)
