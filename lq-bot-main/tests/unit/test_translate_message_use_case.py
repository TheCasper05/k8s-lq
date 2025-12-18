"""Tests unitarios para TranslateMessageUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.translate_message_use_case import TranslateMessageUseCase
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
    return TranslateMessageUseCase(llm=mock_llm, prompt_manager=mock_prompt_manager)


@pytest.mark.asyncio
async def test_execute_simple_translation(use_case, mock_llm, mock_prompt_manager):
    """Test: traducir un mensaje simple."""
    # Arrange
    message_text = "Hello, how are you?"
    target_language = "Spanish"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
        {"properties": {}},  # create_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola, ¿cómo estás?"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={"completion_tokens": 30, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    translation, llm_response = await use_case.execute(
        message_text=message_text,
        target_language=target_language,
    )

    # Assert
    assert isinstance(translation, dict)
    assert translation["id"] == "1"
    assert translation["translation"] == "Hola, ¿cómo estás?"
    assert llm_response == expected_llm_response
    mock_llm.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_execute_with_native_language(use_case, mock_llm, mock_prompt_manager):
    """Test: traducir con idioma nativo especificado."""
    # Arrange
    message_text = "Hello"
    target_language = "Spanish"
    native_language = "English"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
        {"properties": {}},  # create_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=30,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    translation, _ = await use_case.execute(
        message_text=message_text,
        target_language=target_language,
        native_language=native_language,
    )

    # Assert
    assert isinstance(translation, dict)
    assert translation["translation"] == "Hola"
    mock_llm.generate_response.assert_called_once()
