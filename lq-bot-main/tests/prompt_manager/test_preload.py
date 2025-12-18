# tests/prompt_manager/test_init_preload.py
from pathlib import Path

from prompt_manager import FilePromptRepository, InMemoryPromptRepository, preload_files_into_memory


def test_preload_files_into_memory(tmp_path: Path):
    # Crea estructura dummy con versionado
    root = tmp_path / "prompts"
    (root / "corrections" / "v1").mkdir(parents=True)
    (root / "corrections" / "v1" / "grammar.txt").write_text("Hola {user}", encoding="utf-8")

    mem = InMemoryPromptRepository()
    files = FilePromptRepository(root)

    preload_files_into_memory(files, mem)

    # Debe haber registrado el prompt del archivo
    pr = mem.get_prompt("corrections", "grammar", "v1")
    assert pr is not None and "Hola" in pr.content
