"""Tests de integración para el endpoint de text_answer."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.models.message import LLMResponse
from src.interfaces.api.main import create_app


@pytest.fixture
def mock_llm_adapter():
    """Crea un mock del LLM adapter."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm


@pytest.fixture
def mock_prompt_manager():
    """Crea un mock del prompt manager."""
    pm = MagicMock()
    pm.render = MagicMock(return_value="Mocked system prompt")
    return pm


@pytest.fixture
def client(mock_llm_adapter, mock_prompt_manager):
    """Crea un cliente de prueba con LLM mockeado."""
    from src.application.use_cases.generate_text_response_use_case import (
        GenerateTextResponseUseCase,
    )

    # Crear un use case real pero con LLM mockeado
    real_use_case = GenerateTextResponseUseCase(llm=mock_llm_adapter)

    # Patch el factory de LLM ANTES de importar create_app (esto evita crear un LLM real)
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
    ) as mock_llm_factory:
        mock_llm_factory.return_value = mock_llm_adapter

        # Patch las funciones en conversation_service que usan el container
        with patch("src.domain.services.conversation_service.get_prompt_manager") as mock_get_pm:
            mock_get_pm.return_value = mock_prompt_manager
            with patch(
                "src.domain.services.conversation_service.generate_text_response_use_case"
            ) as mock_use_case_func:
                mock_use_case_func.return_value = real_use_case
                app = create_app()
                yield TestClient(app), mock_llm_adapter, mock_prompt_manager


def test_text_answer_success(client):
    """Test: obtener respuesta de texto exitosamente."""
    test_client, mock_llm, _ = client

    # Mock del LLM response
    mock_response = LLMResponse(
        content="Hello! How can I help you today?",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=30,
        finish_reason="stop",
        response_id="resp_123",
        metadata={"completion_tokens": 20, "prompt_tokens": 10},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_response

    # Request con todos los campos requeridos
    payload = {
        "message": "Hello, I need help",
        "scenario_type": "roleplay",
        "response_id": None,
        "theme": "Restaurant conversation",
        "assistant_role": "waiter",
        "user_role": "customer",
        "potential_directions": "ordering food, asking about menu",
        "setting": "Italian restaurant",
        "example": "Customer: I'd like pizza. Waiter: What size?",
        "additional_data": "Use polite language",
        "practice_topic": None,
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Hello! How can I help you today?"
    assert data["model"] == "gpt-4o-mini"
    assert data["total_tokens"] == 30
    assert "response_id" in data

    # Verificar que se llamó al LLM
    mock_llm.generate_response.assert_called_once()
    # Verificar que se pasó el system prompt renderizado
    call_kwargs = mock_llm.generate_response.call_args.kwargs
    assert "system_prompt" in call_kwargs


def test_text_answer_with_teacher_scenario(client):
    """Test: obtener respuesta con escenario de tipo teacher."""
    test_client, mock_llm, _ = client

    mock_response = LLMResponse(
        content="Great! Let's practice verb tenses. Can you tell me what you did yesterday?",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=25,
        finish_reason="stop",
        response_id="resp_123",
        metadata={"completion_tokens": 15, "prompt_tokens": 10},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_response

    payload = {
        "message": "I want to practice English",
        "scenario_type": "teacher",
        "response_id": "resp_123",
        "theme": "Grammar practice",
        "assistant_role": "English teacher",
        "user_role": "student",
        "potential_directions": "verb tenses, past simple, present perfect",
        "setting": "Virtual classroom",
        "example": None,
        "additional_data": "Focus on past simple tense",
        "practice_topic": "verb tenses",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert (
        data["answer"]
        == "Great! Let's practice verb tenses. Can you tell me what you did yesterday?"
    )
    assert "verb tenses" in data["answer"]

    # Verificar que se llamó al LLM
    mock_llm.generate_response.assert_called_once()


def test_text_answer_validation_error_empty_message(client):
    """Test: validación de request con mensaje vacío."""
    test_client, _, _ = client

    payload = {
        "message": "",  # Mensaje vacío
        "scenario_type": "roleplay",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)
    assert response.status_code == 422


def test_text_answer_validation_error_missing_required_fields(client):
    """Test: validación de request con campos requeridos faltantes."""
    test_client, _, _ = client

    # Falta scenario_type
    payload = {
        "message": "Hello",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)
    assert response.status_code == 422


def test_text_answer_validation_error_message_too_long(client):
    """Test: validación de mensaje demasiado largo."""
    test_client, _, _ = client

    payload = {
        "message": "a" * 10001,  # Más de 10000 caracteres
        "scenario_type": "roleplay",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)
    assert response.status_code == 422


def test_text_answer_with_all_optional_fields(client):
    """Test: obtener respuesta con todos los campos opcionales."""
    test_client, mock_llm, _ = client

    mock_response = LLMResponse(
        content="Welcome to our restaurant! What would you like to order?",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=20,
        finish_reason="stop",
        response_id="conv_456",
        metadata={"completion_tokens": 12, "prompt_tokens": 8},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_response

    payload = {
        "message": "I'm looking for a table",
        "scenario_type": "roleplay",
        "response_id": "conv_456",
        "theme": "Restaurant",
        "language": "English",
        "assistant_role": "host",
        "user_role": "guest",
        "potential_directions": "finding table, ordering, asking about menu",
        "setting": "Fine dining restaurant",
        "example": "Guest: Do you have a table? Host: Yes, right this way.",
        "additional_data": "Be very polite and formal",
        "practice_topic": "restaurant vocabulary",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Welcome to our restaurant! What would you like to order?"

    # Verificar que se llamó al LLM
    mock_llm.generate_response.assert_called_once()


def test_text_answer_service_error(client):
    """Test: manejo de error del servicio."""
    from src.domain.exceptions.ai_exceptions import AIProviderError

    test_client, mock_llm, _ = client

    # Simular error del LLM
    mock_llm.generate_response.side_effect = AIProviderError("API key inválida", provider="openai")

    payload = {
        "message": "Test message",
        "scenario_type": "roleplay",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 500
    assert "Error al generar respuesta" in response.json()["detail"]


def test_text_answer_with_different_scenario_types(client):
    """Test: verificar que diferentes tipos de escenario funcionan."""
    test_client, mock_llm, _ = client

    scenario_types = ["roleplay", "teacher", "knowledge"]

    for scenario_type in scenario_types:
        mock_response = LLMResponse(
            content=f"Response for {scenario_type}",
            provider="openai",
            model="gpt-4o-mini",
            tokens_used=15,
            finish_reason="stop",
            response_id=f"resp_{scenario_type}",
            metadata={"completion_tokens": 10, "prompt_tokens": 5},
            created_at=datetime.now(),
        )

        mock_llm.generate_response.return_value = mock_response

        payload = {
            "message": "Test message",
            "scenario_type": scenario_type,
        }

        response = test_client.post("/api/v1/conversation/text_answer", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == f"Response for {scenario_type}"

        # Verificar que se llamó al LLM
        mock_llm.generate_response.assert_called_once()
        mock_llm.reset_mock()


def test_text_answer_with_response_id_for_conversation_history(client):
    """Test: verificar que response_id se pasa correctamente para historial."""
    test_client, mock_llm, _ = client

    mock_response = LLMResponse(
        content="Follow-up response",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=15,
        finish_reason="stop",
        response_id="prev_response_789",
        metadata={"completion_tokens": 10, "prompt_tokens": 5},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_response

    payload = {
        "message": "What about dessert?",
        "scenario_type": "roleplay",
        "response_id": "prev_response_789",
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 200

    # Verificar que response_id se pasó al LLM
    call_kwargs = mock_llm.generate_response.call_args.kwargs
    assert call_kwargs.get("response_id") == "prev_response_789"


def test_text_answer_prompt_manager_called_correctly(client):
    """Test: verificar que el prompt manager se llama con los parámetros correctos."""
    test_client, mock_llm, mock_pm = client

    mock_response = LLMResponse(
        content="Test response",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=10,
        finish_reason="stop",
        response_id="test_resp",
        metadata={"completion_tokens": 6, "prompt_tokens": 4},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_response

    payload = {
        "message": "Hello",
        "scenario_type": "roleplay",
        "theme": "Restaurant",
        "assistant_role": "waiter",
        "user_role": "customer",
        "potential_directions": "ordering",
        "setting": "Italian restaurant",
        "example": "Example",
        "additional_data": "Be polite",
        "practice_topic": None,
    }

    response = test_client.post("/api/v1/conversation/text_answer", json=payload)

    assert response.status_code == 200

    # Verificar que pm.render se llamó con los parámetros correctos
    mock_pm.render.assert_called_once()
    call_args = mock_pm.render.call_args
    assert call_args[0][0] == "conversations"  # category
    assert call_args[0][1] == "roleplay"  # prompt_name (sin sufijo _v1)
    # Verificar que se pasó version en kwargs
    assert "version" in call_args.kwargs
    assert call_args.kwargs["version"] == "v1"  # versión por separado
    assert call_args.kwargs["theme"] == "Restaurant"
    assert call_args.kwargs["assistant_role"] == "waiter"
    assert call_args.kwargs["user_role"] == "customer"
