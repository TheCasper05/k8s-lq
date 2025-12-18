import pytest

from src.prompt_manager.exceptions import MissingTemplateVariablesError, PromptNotFoundError
from src.prompt_manager.manager import PromptManager
from src.prompt_manager.models import PromptDefinition
from src.prompt_manager.repositories.file_repository import FilePromptRepository
from src.prompt_manager.repositories.memory_repository import InMemoryPromptRepository
from src.prompt_manager.templates.engine import TemplateEngine


def test_manager_order_memory_then_file(tmp_path):
    mem = InMemoryPromptRepository({"cat": {"v1": {"name": "M {x}"}}})
    root = tmp_path / "prompts"
    (root / "cat" / "v1").mkdir(parents=True)
    (root / "cat" / "v1" / "name.md").write_text("F {x}", encoding="utf-8")

    pm = PromptManager(
        memory_repo=mem, file_repo=FilePromptRepository(root), template_engine=TemplateEngine()
    )

    # Debe preferir memoria
    assert pm.get("cat", "name").content == "M {x}"
    assert pm.render("cat", "name", x="ok") == "M ok"


def test_manager_not_found_and_missing_vars():
    pm = PromptManager(memory_repo=InMemoryPromptRepository(), template_engine=TemplateEngine())
    with pytest.raises(PromptNotFoundError):
        pm.get("nope", "nope")

    mem = InMemoryPromptRepository({"a": {"v1": {"b": "Hola {who}"}}})
    pm2 = PromptManager(memory_repo=mem, template_engine=TemplateEngine())
    with pytest.raises(MissingTemplateVariablesError):
        pm2.render("a", "b", version="v1")  # falta who


def test_pre_and_post_processors():
    mem = InMemoryPromptRepository({"a": {"v1": {"b": "x"}}})
    pm = PromptManager(memory_repo=mem, template_engine=TemplateEngine())

    def pre_upper(pr: PromptDefinition) -> PromptDefinition:
        return PromptDefinition(key=pr.key, content=pr.content.upper())

    def post_suffix(text: str) -> str:
        return text + "."

    pm.register_preprocessor(pre_upper)
    pm.register_postprocessor(post_suffix)

    assert pm.render("a", "b", version="v1") == "X."


def test_manager_list_categories():
    mem = InMemoryPromptRepository({"a": {"v1": {"b": "X"}}})
    pm = PromptManager(memory_repo=mem, template_engine=TemplateEngine())
    assert pm.list_categories() == ["a"]
    assert pm.list_prompts("a", "v1") == ["b"]
