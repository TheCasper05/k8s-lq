"""
Tests para verificar que los prompts pueden tener contenido dict además de str.
Esto es necesario para soportar esquemas de respuesta estructurados.
"""

import json
from pathlib import Path

from prompt_manager.manager import PromptManager
from prompt_manager.repositories.file_repository import FilePromptRepository
from prompt_manager.repositories.memory_repository import InMemoryPromptRepository
from prompt_manager.templates.engine import TemplateEngine


def test_memory_repo_with_dict_content():
    """Test que InMemoryPromptRepository puede almacenar y recuperar prompts con contenido dict."""
    schema = {
        "type": "object",
        "properties": {"correction": {"type": "string"}, "explanation": {"type": "string"}},
        "required": ["correction"],
    }

    repo = InMemoryPromptRepository(
        {"schemas": {"v1": {"response_schema": schema, "text_prompt": "Corrige {texto}"}}}
    )

    # Verificar que se puede obtener un prompt con dict
    pr_dict = repo.get_prompt("schemas", "response_schema", "v1")
    assert pr_dict is not None
    assert isinstance(pr_dict.content, dict)
    assert pr_dict.content == schema

    # Verificar que también funciona con strings
    pr_str = repo.get_prompt("schemas", "text_prompt", "v1")
    assert pr_str is not None
    assert isinstance(pr_str.content, str)
    assert pr_str.content == "Corrige {texto}"


def test_memory_repo_register_dict():
    """Test que register() acepta contenido dict."""
    repo = InMemoryPromptRepository()
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}

    repo.register("schemas", "test_schema", schema, "v1")

    pr = repo.get_prompt("schemas", "test_schema", "v1")
    assert pr is not None
    assert isinstance(pr.content, dict)
    assert pr.content == schema


def test_memory_repo_bulk_register_with_dict():
    """Test que bulk_register() acepta contenido dict."""
    repo = InMemoryPromptRepository()
    prompts = {
        "schemas": {"v1": {"schema1": {"type": "object"}, "schema2": {"type": "array"}}},
        "texts": {"v1": {"prompt1": "Hola {name}"}},
    }

    repo.bulk_register(prompts)

    pr1 = repo.get_prompt("schemas", "schema1", "v1")
    assert pr1 is not None and isinstance(pr1.content, dict)

    pr2 = repo.get_prompt("texts", "prompt1", "v1")
    assert pr2 is not None and isinstance(pr2.content, str)


def test_file_repo_with_json(tmp_path: Path):
    """Test que FilePromptRepository puede cargar archivos .json como dict."""
    root = tmp_path / "prompts"
    (root / "schemas" / "v1").mkdir(parents=True)

    schema = {"type": "object", "properties": {"result": {"type": "string"}}}

    # Crear archivo JSON
    json_file = root / "schemas" / "v1" / "response.json"
    json_file.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    # Crear también un archivo .md para comparar
    (root / "schemas" / "v1" / "prompt.md").write_text("Test {var}", encoding="utf-8")

    repo = FilePromptRepository(root)

    # Verificar que el JSON se carga como dict
    pr_dict = repo.get_prompt("schemas", "response", "v1")
    assert pr_dict is not None
    assert isinstance(pr_dict.content, dict)
    assert pr_dict.content == schema

    # Verificar que el .md se carga como str
    pr_str = repo.get_prompt("schemas", "prompt", "v1")
    assert pr_str is not None
    assert isinstance(pr_str.content, str)
    assert pr_str.content == "Test {var}"

    # Verificar que list_prompts incluye ambos
    prompts = set(repo.list_prompts("schemas", "v1"))
    assert "response" in prompts
    assert "prompt" in prompts


def test_file_repo_json_in_list_prompts(tmp_path: Path):
    """Test que los archivos .json aparecen en list_prompts."""
    root = tmp_path / "prompts"
    (root / "schemas" / "v1").mkdir(parents=True)

    (root / "schemas" / "v1" / "schema1.json").write_text('{"type": "object"}', encoding="utf-8")
    (root / "schemas" / "v1" / "schema2.json").write_text('{"type": "array"}', encoding="utf-8")

    repo = FilePromptRepository(root)
    prompts = set(repo.list_prompts("schemas", "v1"))
    assert "schema1" in prompts
    assert "schema2" in prompts


def test_manager_render_with_dict():
    """Test que PromptManager.render() devuelve dict directamente cuando el contenido es dict."""
    schema = {"type": "object", "properties": {"answer": {"type": "string"}}}

    mem = InMemoryPromptRepository(
        {"schemas": {"v1": {"response": schema, "text_template": "Hola {user}"}}}
    )

    pm = PromptManager(memory_repo=mem, template_engine=TemplateEngine())

    # Cuando el contenido es dict, render() lo devuelve sin procesar
    result = pm.render("schemas", "response", version="v1")
    assert isinstance(result, dict)
    assert result == schema

    # Cuando el contenido es str, render() lo procesa normalmente
    result_str = pm.render("schemas", "text_template", version="v1", user="Mundo")
    assert isinstance(result_str, str)
    assert result_str == "Hola Mundo"


def test_manager_get_with_dict():
    """Test que PromptManager.get() devuelve PromptDefinition con contenido dict."""
    schema = {"type": "object", "properties": {"x": {"type": "string"}}}

    mem = InMemoryPromptRepository({"schemas": {"v1": {"test": schema}}})

    pm = PromptManager(memory_repo=mem)
    pr = pm.get("schemas", "test", "v1")

    assert isinstance(pr.content, dict)
    assert pr.content == schema


def test_manager_dict_not_rendered():
    """Test que los dicts no pasan por el template engine ni postprocessors."""
    schema = {"type": "object"}

    mem = InMemoryPromptRepository({"schemas": {"v1": {"test": schema}}})

    pm = PromptManager(memory_repo=mem, template_engine=TemplateEngine())

    # Registrar un postprocessor que modificaría strings
    def postprocessor(text: str) -> str:
        return text.upper()

    pm.register_postprocessor(postprocessor)

    # El dict no debe ser afectado por el postprocessor
    result = pm.render("schemas", "test", version="v1")
    assert result == schema
    assert isinstance(result, dict)


def test_preload_files_with_json(tmp_path: Path):
    """Test que preload_files_into_memory carga archivos .json correctamente."""
    from prompt_manager import preload_files_into_memory

    root = tmp_path / "prompts"
    (root / "schemas" / "v1").mkdir(parents=True)

    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    (root / "schemas" / "v1" / "response.json").write_text(json.dumps(schema), encoding="utf-8")
    (root / "schemas" / "v1" / "prompt.md").write_text("Test {x}", encoding="utf-8")

    files = FilePromptRepository(root)
    mem = InMemoryPromptRepository()

    preload_files_into_memory(files, mem)

    # Verificar que el JSON se cargó como dict
    pr_dict = mem.get_prompt("schemas", "response", "v1")
    assert pr_dict is not None
    assert isinstance(pr_dict.content, dict)
    assert pr_dict.content == schema

    # Verificar que el .md se cargó como str
    pr_str = mem.get_prompt("schemas", "prompt", "v1")
    assert pr_str is not None
    assert isinstance(pr_str.content, str)
    assert pr_str.content == "Test {x}"


def test_mixed_content_in_same_category():
    """Test que se pueden mezclar prompts str y dict en la misma categoría."""
    repo = InMemoryPromptRepository(
        {
            "mixed": {
                "v1": {
                    "text_prompt": "Corrige {texto}",
                    "schema_prompt": {
                        "type": "object",
                        "properties": {"result": {"type": "string"}},
                    },
                    "another_text": "Hola {name}",
                }
            }
        }
    )

    pr1 = repo.get_prompt("mixed", "text_prompt", "v1")
    assert isinstance(pr1.content, str)

    pr2 = repo.get_prompt("mixed", "schema_prompt", "v1")
    assert isinstance(pr2.content, dict)

    pr3 = repo.get_prompt("mixed", "another_text", "v1")
    assert isinstance(pr3.content, str)

    # Verificar que todos están listados
    prompts = set(repo.list_prompts("mixed", "v1"))
    assert "text_prompt" in prompts
    assert "schema_prompt" in prompts
    assert "another_text" in prompts
