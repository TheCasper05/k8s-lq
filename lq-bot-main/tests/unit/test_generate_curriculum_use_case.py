"""Tests unitarios para CurriculumGeneratorUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.generate_curriculum_use_case import CurriculumGeneratorUseCase
from src.domain.models.curriculum import Curriculum, CurriculumMetadata
from src.domain.models.message import LLMResponse


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
def use_case(mock_llm, mock_prompt_manager):
    """Crea una instancia del caso de uso con dependencias mockeadas."""
    return CurriculumGeneratorUseCase(llm=mock_llm, prompt_manager=mock_prompt_manager)


@pytest.mark.asyncio
async def test_execute_generates_curriculum(use_case, mock_llm, mock_prompt_manager):
    """Test: generar un currículo completo."""
    # Arrange
    level = "A1"
    language = "Spanish"
    topics = ["greetings", "numbers"]

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "Curriculum system prompt",  # create_system
        "Course description: Curso de Spanish nivel A1. sobre los siguientes temas: greetings, numbers.",  # create_user
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "submodules": {"type": "array"},
            },
        },  # create_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"name": "Curso de Español Básico", "description": "Curso introductorio de español", "submodules": [{"name": "Saludos y Presentaciones", "scenarios": ["El escenario trata sobre saludar a alguien por primera vez"]}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=150,
        finish_reason="stop",
        metadata={"completion_tokens": 100, "prompt_tokens": 50},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    curriculum, curriculum_metadata = await use_case.execute(
        level=level,
        language=language,
        topics=topics,
    )

    # Assert
    assert isinstance(curriculum, Curriculum)
    assert curriculum.name == "Curso de Español Básico"
    assert curriculum.description == "Curso introductorio de español"
    assert len(curriculum.submodules) == 1
    assert curriculum.submodules[0].name == "Saludos y Presentaciones"
    assert isinstance(curriculum_metadata, CurriculumMetadata)
    assert curriculum_metadata.provider == "openai"
    assert curriculum_metadata.model == "gpt-4o-mini"
    assert curriculum_metadata.tokens_used == 150
    mock_llm.generate_response.assert_called_once()
    assert mock_prompt_manager.render.call_count == 3


@pytest.mark.asyncio
async def test_execute_without_topics(use_case, mock_llm, mock_prompt_manager):
    """Test: generar currículo sin topics especificados."""
    # Arrange
    level = "B1"
    language = "English"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "Curriculum system prompt",
        "Course description: Curso de English nivel B1.",
        {"type": "object", "properties": {}},
    ]

    expected_llm_response = LLMResponse(
        content='{"name": "Intermediate English", "description": "Intermediate level course", "submodules": []}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    curriculum, curriculum_metadata = await use_case.execute(
        level=level,
        language=language,
        topics=None,
    )

    # Assert
    assert isinstance(curriculum, Curriculum)
    assert curriculum.name == "Intermediate English"
    assert isinstance(curriculum_metadata, CurriculumMetadata)
    mock_llm.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_execute_handles_json_decode_error(use_case, mock_llm, mock_prompt_manager):
    """Test: manejar error de parsing JSON cuando el LLM devuelve texto adicional."""
    # Arrange
    level = "A2"
    language = "French"

    mock_prompt_manager.render.side_effect = [
        "Curriculum system prompt",
        "Course description: Curso de French nivel A2.",
        {"type": "object", "properties": {}},
    ]

    # LLM devuelve JSON con texto adicional
    expected_llm_response = LLMResponse(
        content='Here is the curriculum:\n{"name": "French Course", "description": "A course", "submodules": []}\nEnd of response.',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    curriculum, curriculum_metadata = await use_case.execute(
        level=level,
        language=language,
    )

    # Assert
    assert isinstance(curriculum, Curriculum)
    assert curriculum.name == "French Course"
    assert isinstance(curriculum_metadata, CurriculumMetadata)


@pytest.mark.asyncio
async def test_execute_raises_error_on_invalid_json(use_case, mock_llm, mock_prompt_manager):
    """Test: lanzar error cuando no se puede parsear JSON."""
    # Arrange
    level = "C1"
    language = "German"

    mock_prompt_manager.render.side_effect = [
        "Curriculum system prompt",
        "Course description: Curso de German nivel C1.",
        {"type": "object", "properties": {}},
    ]

    # LLM devuelve contenido que no es JSON válido
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
        await use_case.execute(level=level, language=language)
