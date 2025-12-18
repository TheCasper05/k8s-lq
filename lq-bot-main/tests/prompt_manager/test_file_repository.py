from pathlib import Path

from prompt_manager.repositories.file_repository import FilePromptRepository


def test_file_repo_ok(tmp_path: Path):
    root = tmp_path / "prompts"
    (root / "corrections" / "v1").mkdir(parents=True)
    (root / "corrections" / "v1" / "grammar.md").write_text("Fix {text}", encoding="utf-8")

    repo = FilePromptRepository(root)
    assert "corrections" in set(repo.list_categories())
    assert "grammar" in set(repo.list_prompts("corrections", "v1"))

    pr = repo.get_prompt("corrections", "grammar", "v1")
    assert pr is not None and pr.content == "Fix {text}"


def test_file_repo_missing_returns_none(tmp_path: Path):
    repo = FilePromptRepository(tmp_path / "prompts")
    assert repo.get_prompt("nope", "nope", "v1") is None
    assert repo.list_prompts("nope", "v1") == []
