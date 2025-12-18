import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.models.message import LLMResponse
from src.multi_agent_manager.manager import MultiAgentManager
from src.multi_agent_manager.repositories import FileProcessRepository
from src.prompt_manager.manager import PromptManager
from src.prompt_manager.repositories import InMemoryPromptRepository
from src.prompt_manager.templates import TemplateEngine


@pytest.fixture
def prompt_manager():
    prompts = {
        "test": {
            "v1": {
                "prep_user": "User request: {user_request}",
                "build_user": "Context={context};Lang={language}",
            }
        }
    }
    return PromptManager(
        memory_repo=InMemoryPromptRepository(prompts),
        template_engine=TemplateEngine(),
    )


@pytest.mark.asyncio
async def test_execute_merges_json_and_renders_next_step(prompt_manager):
    llm = MagicMock()
    llm.generate_response = AsyncMock()

    # Primera respuesta: JSON que se fusionará al contexto
    llm.generate_response.side_effect = [
        LLMResponse(
            content=json.dumps({"context": "order tacos", "language": "Spanish"}),
            provider="dummy",
            model="dummy",
            tokens_used=1,
            created_at=datetime.now(),
        ),
        LLMResponse(
            content="final-output",
            provider="dummy",
            model="dummy",
            tokens_used=1,
            created_at=datetime.now(),
        ),
    ]

    process_def = [
        {
            "id": "prepare",
            "user_prompt": {"category": "test", "name": "prep_user", "version": "v1"},
        },
        {
            "id": "build",
            "user_prompt": {"category": "test", "name": "build_user", "version": "v1"},
        },
    ]

    mam = MultiAgentManager(prompt_manager=prompt_manager, llm=llm)

    results = await mam.execute(
        process_definition=process_def, initial_context={"user_request": "Please help"}
    )

    # Se llamaron dos veces al LLM
    assert llm.generate_response.await_count == 2

    # El segundo prompt se renderizó con los datos del JSON fusionado
    second_call = llm.generate_response.await_args_list[1]
    rendered_prompt = second_call.kwargs["messages"][0].content
    assert rendered_prompt == "Context=order tacos;Lang=Spanish"

    # Resultados coherentes
    assert len(results) == 2
    assert results[0].step_id == "prepare"
    assert results[1].step_id == "build"
    assert results[1].llm_response.content == "final-output"


@pytest.mark.asyncio
async def test_execute_from_repo_loads_process(tmp_path: Path, prompt_manager):
    llm = MagicMock()
    llm.generate_response = AsyncMock(
        return_value=LLMResponse(
            content="done",
            provider="dummy",
            model="dummy",
            tokens_used=1,
            created_at=datetime.now(),
        )
    )

    # Crear proceso en disco
    root = tmp_path / "processes"
    proc_dir = root / "scenarios" / "v1"
    proc_dir.mkdir(parents=True)
    (proc_dir / "flow.json").write_text(
        json.dumps(
            [
                {
                    "id": "only",
                    "user_prompt": {"category": "test", "name": "prep_user", "version": "v1"},
                }
            ]
        ),
        encoding="utf-8",
    )

    repo = FileProcessRepository(root)
    mam = MultiAgentManager(prompt_manager=prompt_manager, llm=llm, process_repository=repo)

    results = await mam.execute_from_repo(
        category="scenarios",
        name="flow",
        version="v1",
        initial_context={"user_request": "Hi"},
    )

    llm.generate_response.assert_awaited_once()
    assert len(results) == 1
    assert results[0].step_id == "only"
