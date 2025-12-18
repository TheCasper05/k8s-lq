"""Tests unitarios para CreateScenarioUseCase."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.create_scenario_use_case import CreateScenarioUseCase
from src.domain.models.message import LLMResponse
from src.domain.models.scenario import Scenario, ScenarioMetadata
from src.multi_agent_manager.models import AgentStepResult


@pytest.fixture
def mock_llm():
    """Crea un mock del LLMPort."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    llm.get_provider_name = MagicMock(return_value="openai")
    llm.get_model_info = MagicMock(return_value={"name": "gpt-4o-mini"})
    return llm


@pytest.fixture
def mock_prompt_manager():
    """Crea un mock del PromptManager."""
    pm = MagicMock()
    pm.render = MagicMock()
    return pm


@pytest.fixture
def mock_multi_agent_manager():
    """Crea un mock del MultiAgentManager."""
    mam = MagicMock()
    mam.execute_from_repo = AsyncMock()
    return mam


@pytest.fixture
def mock_settings_multi_agent():
    """Crea un mock de Settings con multi-agent habilitado."""
    settings = MagicMock()
    settings.scenario_multi_agent = True
    return settings


@pytest.fixture
def mock_settings_single_llm():
    """Crea un mock de Settings con multi-agent deshabilitado."""
    settings = MagicMock()
    settings.scenario_multi_agent = False
    return settings


@pytest.fixture
def use_case_multi_agent(
    mock_llm, mock_prompt_manager, mock_multi_agent_manager, mock_settings_multi_agent
):
    """Crea una instancia del caso de uso con multi-agent habilitado."""
    return CreateScenarioUseCase(
        llm=mock_llm,
        prompt_manager=mock_prompt_manager,
        multi_agent_manager=mock_multi_agent_manager,
        settings=mock_settings_multi_agent,
    )


@pytest.fixture
def use_case_single_llm(mock_llm, mock_prompt_manager, mock_settings_single_llm):
    """Crea una instancia del caso de uso con single LLM."""
    return CreateScenarioUseCase(
        llm=mock_llm,
        prompt_manager=mock_prompt_manager,
        multi_agent_manager=None,
        settings=mock_settings_single_llm,
    )


@pytest.fixture
def sample_scenario_dict():
    """Retorna un diccionario de ejemplo de escenario."""
    return {
        "title": "Ordering Tacos in Mexico City",
        "assistant_gender": "male",
        "scenario_type": "roleplay",
        "practice_topic": "food ordering",
        "complete_description": "You are a tourist ordering tacos at a mercado.",
        "theme": "Ordering Food at a Traditional Market",
        "assistant_role": "friendly waiter",
        "user_role": "tourist",
        "setting": "A traditional mercado in Mexico City",
        "potential_directions": "Asking about ingredients, Ordering different dishes, Discussing prices, Learning food vocabulary, Cultural exchange",
        "example": "Assistant: ¡Bienvenido! ¿Qué le gustaría ordenar? User: Quisiera tres tacos, por favor.",
        "additional_data": [],
        "appropriate": True,
    }


# ========== Tests para Multi-Agent ==========


@pytest.mark.asyncio
async def test_execute_multi_agent_creates_scenario(
    use_case_multi_agent, mock_multi_agent_manager, sample_scenario_dict
):
    """Test: crear escenario usando multi-agent manager."""
    # Arrange
    user_request = "I want to practice ordering tacos in Spanish"

    # Mock del resultado del multi-agent manager
    llm_response = LLMResponse(
        content=json.dumps(sample_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=500,
        finish_reason="stop",
        metadata={"completion_tokens": 400, "prompt_tokens": 100},
        created_at=datetime.now(),
    )

    step_result = AgentStepResult(
        step_id="build_scenario",
        output_key="scenario_json",
        llm_response=llm_response,
        rendered_user_prompt="...",
        rendered_system_prompt="...",
        response_schema=None,
        error=None,
    )

    mock_multi_agent_manager.execute_from_repo.return_value = [step_result]

    # Act
    scenario, scenario_metadata = await use_case_multi_agent.execute(user_request=user_request)

    # Assert
    assert isinstance(scenario, Scenario)
    assert scenario.title == "Ordering Tacos in Mexico City"
    assert scenario.scenario_type == "roleplay"
    assert scenario.assistant_role == "friendly waiter"
    assert isinstance(scenario_metadata, ScenarioMetadata)
    assert scenario_metadata.provider == "openai"
    assert scenario_metadata.model == "gpt-4o-mini"
    assert scenario_metadata.tokens_used == 500

    mock_multi_agent_manager.execute_from_repo.assert_called_once_with(
        category="scenarios",
        name="create_multi_agent_process",
        version="v1",
        initial_context={"user_request": user_request},
        llm_defaults={"temperature": 0.7, "max_tokens": 2000},
    )


@pytest.mark.asyncio
async def test_execute_multi_agent_with_custom_params(
    use_case_multi_agent, mock_multi_agent_manager, sample_scenario_dict
):
    """Test: crear escenario con multi-agent usando parámetros personalizados."""
    # Arrange
    user_request = "Create a scenario for practicing French"
    temperature = 0.5
    max_tokens = 3000

    llm_response = LLMResponse(
        content=json.dumps(sample_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=600,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    step_result = AgentStepResult(
        step_id="build_scenario",
        output_key="scenario_json",
        llm_response=llm_response,
        rendered_user_prompt="...",
        rendered_system_prompt="...",
        response_schema=None,
        error=None,
    )

    mock_multi_agent_manager.execute_from_repo.return_value = [step_result]

    # Act
    scenario, _scenario_metadata = await use_case_multi_agent.execute(
        user_request=user_request, temperature=temperature, max_tokens=max_tokens
    )

    # Assert
    assert isinstance(scenario, Scenario)
    mock_multi_agent_manager.execute_from_repo.assert_called_once_with(
        category="scenarios",
        name="create_multi_agent_process",
        version="v1",
        initial_context={"user_request": user_request},
        llm_defaults={"temperature": temperature, "max_tokens": max_tokens},
    )


@pytest.mark.asyncio
async def test_execute_multi_agent_raises_error_on_step_error(
    use_case_multi_agent, mock_multi_agent_manager
):
    """Test: lanzar error cuando el step del multi-agent falla."""
    # Arrange
    user_request = "Create a scenario"

    step_result = AgentStepResult(
        step_id="build_scenario",
        output_key="scenario_json",
        llm_response=None,
        rendered_user_prompt="...",
        rendered_system_prompt="...",
        response_schema=None,
        error=ValueError("LLM error"),
    )

    mock_multi_agent_manager.execute_from_repo.return_value = [step_result]

    # Act & Assert
    with pytest.raises(ValueError, match="Error en el proceso multi-agent"):
        await use_case_multi_agent.execute(user_request=user_request)


@pytest.mark.asyncio
async def test_execute_multi_agent_raises_error_on_no_response(
    use_case_multi_agent, mock_multi_agent_manager
):
    """Test: lanzar error cuando no hay respuesta del LLM."""
    # Arrange
    user_request = "Create a scenario"

    step_result = AgentStepResult(
        step_id="build_scenario",
        output_key="scenario_json",
        llm_response=None,
        rendered_user_prompt="...",
        rendered_system_prompt="...",
        response_schema=None,
        error=None,
    )

    mock_multi_agent_manager.execute_from_repo.return_value = [step_result]

    # Act & Assert
    with pytest.raises(ValueError, match="No se obtuvo respuesta del LLM"):
        await use_case_multi_agent.execute(user_request=user_request)


# ========== Tests para Single LLM ==========


@pytest.mark.asyncio
async def test_execute_single_llm_creates_scenario(
    use_case_single_llm, mock_llm, mock_prompt_manager, sample_scenario_dict
):
    """Test: crear escenario usando single LLM."""
    # Arrange
    user_request = "I want to practice ordering food in French"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are a scenario builder...",  # create_system
        f"Scenario request: '{user_request}' Language: English",  # create_user
        {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "scenario_type": {"type": "string"},
            },
        },  # create_response_schema
    ]

    expected_llm_response = LLMResponse(
        content=json.dumps(sample_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=400,
        finish_reason="stop",
        metadata={"completion_tokens": 300, "prompt_tokens": 100},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    scenario, scenario_metadata = await use_case_single_llm.execute(user_request=user_request)

    # Assert
    assert isinstance(scenario, Scenario)
    assert scenario.title == "Ordering Tacos in Mexico City"
    assert isinstance(scenario_metadata, ScenarioMetadata)
    assert scenario_metadata.provider == "openai"
    assert scenario_metadata.tokens_used == 400

    mock_llm.generate_response.assert_called_once()
    assert mock_prompt_manager.render.call_count == 3


@pytest.mark.asyncio
async def test_execute_single_llm_with_custom_params(
    use_case_single_llm, mock_llm, mock_prompt_manager, sample_scenario_dict
):
    """Test: crear escenario con single LLM usando parámetros personalizados."""
    # Arrange
    user_request = "Create a scenario"
    temperature = 0.8
    max_tokens = 2500

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        f"User prompt: {user_request}",
        {"type": "object"},
    ]

    expected_llm_response = LLMResponse(
        content=json.dumps(sample_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=500,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    scenario, _scenario_metadata = await use_case_single_llm.execute(
        user_request=user_request, temperature=temperature, max_tokens=max_tokens
    )

    # Assert
    assert isinstance(scenario, Scenario)
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["temperature"] == temperature
    assert call_args.kwargs["max_tokens"] == max_tokens


@pytest.mark.asyncio
async def test_execute_single_llm_handles_json_with_text(
    use_case_single_llm, mock_llm, mock_prompt_manager, sample_scenario_dict
):
    """Test: manejar JSON envuelto en texto adicional."""
    # Arrange
    user_request = "Create a scenario"

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object"},
    ]

    # LLM devuelve JSON con texto adicional
    json_with_text = f"Here is the scenario:\n{json.dumps(sample_scenario_dict)}\nEnd of response."
    expected_llm_response = LLMResponse(
        content=json_with_text,
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=400,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    scenario, _scenario_metadata = await use_case_single_llm.execute(user_request=user_request)

    # Assert
    assert isinstance(scenario, Scenario)
    assert scenario.title == "Ordering Tacos in Mexico City"


@pytest.mark.asyncio
async def test_execute_single_llm_raises_error_on_invalid_json(
    use_case_single_llm, mock_llm, mock_prompt_manager
):
    """Test: lanzar error cuando no se puede parsear JSON."""
    # Arrange
    user_request = "Create a scenario"

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object"},
    ]

    expected_llm_response = LLMResponse(
        content="This is not valid JSON at all",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act & Assert
    with pytest.raises(ValueError, match="No se pudo parsear la respuesta como JSON"):
        await use_case_single_llm.execute(user_request=user_request)


# ========== Tests de conversión ==========


@pytest.mark.asyncio
async def test_dict_to_scenario_converts_all_fields(
    use_case_single_llm, mock_llm, mock_prompt_manager
):
    """Test: verificar que todos los campos se convierten correctamente."""
    # Arrange
    user_request = "Create a scenario"
    full_scenario_dict = {
        "title": "Test Scenario",
        "assistant_gender": "female",
        "scenario_type": "teacher",
        "practice_topic": "grammar",
        "complete_description": "Test description",
        "theme": "Test Theme",
        "assistant_role": "teacher",
        "user_role": "student",
        "setting": "classroom",
        "potential_directions": "dir1, dir2, dir3",
        "example": "Example dialogue",
        "additional_data": ["data1", "data2"],
        "appropriate": False,
    }

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object"},
    ]

    expected_llm_response = LLMResponse(
        content=json.dumps(full_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    scenario, _ = await use_case_single_llm.execute(user_request=user_request)

    # Assert
    assert scenario.title == "Test Scenario"
    assert scenario.assistant_gender == "female"
    assert scenario.scenario_type == "teacher"
    assert scenario.practice_topic == "grammar"
    assert scenario.complete_description == "Test description"
    assert scenario.theme == "Test Theme"
    assert scenario.assistant_role == "teacher"
    assert scenario.user_role == "student"
    assert scenario.setting == "classroom"
    assert scenario.potential_directions == "dir1, dir2, dir3"
    assert scenario.example == "Example dialogue"
    assert scenario.additional_data == ["data1", "data2"]
    assert scenario.appropriate is False


@pytest.mark.asyncio
async def test_dict_to_scenario_uses_defaults_for_missing_fields(
    use_case_single_llm, mock_llm, mock_prompt_manager
):
    """Test: usar valores por defecto cuando faltan campos."""
    # Arrange
    user_request = "Create a scenario"
    minimal_scenario_dict = {
        "title": "Minimal Scenario",
        "complete_description": "Description",
        "theme": "Theme",
        "assistant_role": "assistant",
        "user_role": "user",
        "setting": "setting",
        "potential_directions": "directions",
        "example": "example",
        "additional_data": [],
        "appropriate": True,
    }

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object"},
    ]

    expected_llm_response = LLMResponse(
        content=json.dumps(minimal_scenario_dict),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    scenario, _ = await use_case_single_llm.execute(user_request=user_request)

    # Assert
    assert scenario.title == "Minimal Scenario"
    assert scenario.assistant_gender == "male"  # default
    assert scenario.scenario_type == "roleplay"  # default
    assert scenario.practice_topic == "all"  # default
