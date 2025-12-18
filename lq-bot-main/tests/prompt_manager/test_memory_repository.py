from prompt_manager.repositories.memory_repository import InMemoryPromptRepository


def test_memory_repo_basic_and_register():
    repo = InMemoryPromptRepository(
        {
            "scenarios": {"v1": {"create": "Hola {user}"}},
            "corrections": {"v1": {"grammar": "Corrige {texto}"}},
        }
    )
    assert set(repo.list_categories()) == {"scenarios", "corrections"}
    assert set(repo.list_prompts("scenarios", "v1")) == {"create"}

    pr = repo.get_prompt("scenarios", "create", "v1")
    assert pr is not None and pr.content == "Hola {user}"

    # register en caliente
    repo.register("scenarios", "review", "Revisa {user}", "v1")
    assert "review" in set(repo.list_prompts("scenarios", "v1"))


def test_memory_repo_has_prompt_and_bulk():
    repo = InMemoryPromptRepository()
    repo.bulk_register({"a": {"v1": {"b": "X {v}"}}})
    assert repo.has_prompt("a", "b", "v1")
