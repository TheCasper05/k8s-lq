"""Tests unitarios para GenerateConversationSuggestionsUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.generate_conversation_suggestions_use_case import (
    GenerateConversationSuggestionsUseCase,
)
from src.domain.models.message import LLMResponse, Message


@pytest.fixture
def mock_llm():
    """Crea un mock del LLMPort."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm


@pytest.fixture
def use_case(mock_llm):
    """Crea una instancia del caso de uso con dependencias mockeadas."""
    return GenerateConversationSuggestionsUseCase(llm=mock_llm)


@pytest.mark.asyncio
async def test_execute_simple_message(use_case, mock_llm):
    """Test: generar sugerencias con un mensaje simple."""
    # Arrange
    user_message = "Hola, ¿cómo estás?"
    expected_response = LLMResponse(
        content='{"suggestions": ["¡Hola! Estoy bien, gracias", "Muy bien, ¿y tú?", "Todo perfecto, gracias"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={"completion_tokens": 30, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(user_message=user_message)

    # Assert
    assert response == expected_response
    mock_llm.generate_response.assert_called_once()

    # Verificar que se llamó con los parámetros correctos
    call_args = mock_llm.generate_response.call_args
    assert len(call_args.kwargs["messages"]) == 1
    assert call_args.kwargs["messages"][0].role == "user"
    assert call_args.kwargs["messages"][0].content == user_message
    assert call_args.kwargs["temperature"] == 0.7
    assert call_args.kwargs["max_tokens"] == 1_000
    assert call_args.kwargs.get("json_schema") is None


@pytest.mark.asyncio
async def test_execute_with_system_prompt(use_case, mock_llm):
    """Test: generar sugerencias con system prompt."""
    # Arrange
    user_message = "¿Qué puedo decir?"
    system_prompt = "Eres un asistente que genera sugerencias de respuestas."

    expected_response = LLMResponse(
        content='{"suggestions": ["Sugerencia 1", "Sugerencia 2", "Sugerencia 3"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=30,
        finish_reason="stop",
        metadata={"completion_tokens": 10, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(user_message=user_message, system_prompt=system_prompt)

    # Assert
    assert response == expected_response

    # Verificar que se pasó el system prompt
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["system_prompt"] == system_prompt


@pytest.mark.asyncio
async def test_execute_with_response_schema(use_case, mock_llm):
    """Test: generar sugerencias con response schema."""
    # Arrange
    user_message = "¿Qué puedo decir?"
    response_schema = {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["suggestions"],
    }

    expected_response = LLMResponse(
        content='{"suggestions": ["Opción 1", "Opción 2", "Opción 3"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=40,
        finish_reason="stop",
        metadata={"completion_tokens": 20, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(user_message=user_message, response_schema=response_schema)

    # Assert
    assert response == expected_response

    # Verificar que se pasó el response_schema como json_schema
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["json_schema"] == response_schema


@pytest.mark.asyncio
async def test_execute_with_custom_parameters(use_case, mock_llm):
    """Test: generar sugerencias con parámetros personalizados."""
    # Arrange
    user_message = "Genera sugerencias creativas"
    temperature = 1.2
    max_tokens = 500

    expected_response = LLMResponse(
        content='{"suggestions": ["Sugerencia creativa 1", "Sugerencia creativa 2", "Sugerencia creativa 3"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={"completion_tokens": 80, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(
        user_message=user_message, temperature=temperature, max_tokens=max_tokens
    )

    # Assert
    assert response == expected_response

    # Verificar parámetros personalizados
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["temperature"] == temperature
    assert call_args.kwargs["max_tokens"] == max_tokens


@pytest.mark.asyncio
async def test_execute_creates_user_message_with_correct_structure(use_case, mock_llm):
    """Test: verificar que se crea correctamente el mensaje del usuario."""
    # Arrange
    user_message = "Test message"
    mock_llm.generate_response.return_value = LLMResponse(
        content='{"suggestions": ["Test 1", "Test 2", "Test 3"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=10,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    # Act
    await use_case.execute(user_message=user_message)

    # Assert
    call_args = mock_llm.generate_response.call_args
    user_msg = call_args.kwargs["messages"][0]

    assert isinstance(user_msg, Message)
    assert user_msg.role == "user"
    assert user_msg.content == user_message
    assert isinstance(user_msg.timestamp, datetime)
    assert user_msg.metadata is None


@pytest.mark.asyncio
async def test_execute_with_system_prompt_and_schema(use_case, mock_llm):
    """Test: generar sugerencias con system prompt y response schema."""
    # Arrange
    user_message = "¿Qué puedo responder?"
    system_prompt = "Genera 3 sugerencias de respuestas."
    response_schema = {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
            }
        },
        "required": ["suggestions"],
        "additionalProperties": False,
    }

    expected_response = LLMResponse(
        content='{"suggestions": ["Respuesta 1", "Respuesta 2", "Respuesta 3"]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={"completion_tokens": 30, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(
        user_message=user_message,
        system_prompt=system_prompt,
        response_schema=response_schema,
    )

    # Assert
    assert response == expected_response

    # Verificar que se pasaron ambos parámetros
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["system_prompt"] == system_prompt
    assert call_args.kwargs["json_schema"] == response_schema
