"""Tests unitarios para GenerateTextResponseUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.generate_text_response_use_case import (
    GenerateTextResponseUseCase,
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
    return GenerateTextResponseUseCase(llm=mock_llm)


@pytest.mark.asyncio
async def test_execute_simple_message(use_case, mock_llm):
    """Test: generar respuesta con un mensaje simple."""
    # Arrange
    user_message = "Hola, ¿cómo estás?"
    expected_response = LLMResponse(
        content="¡Hola! Estoy bien, gracias por preguntar.",
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


@pytest.mark.asyncio
async def test_execute_with_conversation_history(use_case, mock_llm):
    """Test: generar respuesta con historial de conversación."""
    # Arrange
    conversation_history = [
        Message(role="user", content="¿Cuál es la capital de Francia?", timestamp=datetime.now()),
        Message(
            role="assistant", content="La capital de Francia es París.", timestamp=datetime.now()
        ),
    ]
    user_message = "¿Y de España?"

    expected_response = LLMResponse(
        content="La capital de España es Madrid.",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=40,
        finish_reason="stop",
        metadata={"completion_tokens": 20, "prompt_tokens": 20},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_response

    # Act
    response = await use_case.execute(
        user_message=user_message, conversation_history=conversation_history
    )

    # Assert
    assert response == expected_response

    # Verificar que se pasó el historial completo
    call_args = mock_llm.generate_response.call_args
    messages = call_args.kwargs["messages"]
    assert len(messages) == 3  # 2 del historial + 1 nuevo
    assert messages[0].content == "¿Cuál es la capital de Francia?"
    assert messages[1].content == "La capital de Francia es París."
    assert messages[2].content == "¿Y de España?"


@pytest.mark.asyncio
async def test_execute_with_system_prompt(use_case, mock_llm):
    """Test: generar respuesta con system prompt."""
    # Arrange
    user_message = "Traduce al inglés: Hola mundo"
    system_prompt = "Eres un traductor profesional de español a inglés."

    expected_response = LLMResponse(
        content="Hello world",
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
async def test_execute_with_custom_parameters(use_case, mock_llm):
    """Test: generar respuesta con parámetros personalizados."""
    # Arrange
    user_message = "Escribe un poema corto"
    temperature = 1.2
    max_tokens = 500

    expected_response = LLMResponse(
        content="Poema generado...",
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
        content="Response",
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
