"""Tests unitarios para BatchTranslateUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.batch_translate_use_case import BatchTranslateUseCase
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
    return BatchTranslateUseCase(llm=mock_llm, prompt_manager=mock_prompt_manager)


@pytest.mark.asyncio
async def test_execute_batch_translation(use_case, mock_llm, mock_prompt_manager):
    """Test: traducir un array de objetos JSON."""
    # Arrange
    data = [{"id": "1", "word": "Hello"}, {"id": "2", "word": "World"}]
    target_language = "Spanish"

    response_schema = {
        "properties": {
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}, "translation": {"type": "string"}},
                },
            }
        }
    }

    system_prompt = "Translate to Spanish"
    user_prompt = f"User input: {data}, Language: {target_language}."

    mock_prompt_manager.render.side_effect = [
        response_schema,  # create_response_schema
        system_prompt,  # create_system
        user_prompt,  # create_user
    ]

    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola"}, {"id": "2", "translation": "Mundo"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={"completion_tokens": 50, "prompt_tokens": 50},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    result, llm_response = await use_case.execute(
        data=data,
        target_language=target_language,
    )

    # Assert
    assert "translations" in result
    assert len(result["translations"]) == 2
    assert result["translations"][0]["id"] == "1"
    assert result["translations"][0]["translation"] == "Hola"
    assert llm_response == expected_llm_response
    mock_llm.generate_response.assert_called_once()
    assert mock_prompt_manager.render.call_count == 3


@pytest.mark.asyncio
async def test_execute_with_native_language(use_case, mock_llm, mock_prompt_manager):
    """Test: traducir con idioma nativo especificado."""
    # Arrange
    data = [{"id": "1", "word": "Hello"}]
    target_language = "Spanish"
    native_language = "English"

    mock_prompt_manager.render.side_effect = [
        {},  # response_schema
        "Translate",  # system_prompt
        "User input",  # user_prompt
    ]

    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    result, _ = await use_case.execute(
        data=data,
        target_language=target_language,
        native_language=native_language,
    )

    # Assert
    assert "translations" in result
    mock_llm.generate_response.assert_called_once()
