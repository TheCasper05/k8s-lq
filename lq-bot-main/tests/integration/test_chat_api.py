"""Tests de integración para el endpoint de chat."""

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
def client(mock_llm_adapter):
    """Crea un cliente de prueba con dependencias mockeadas."""
    # Patch el factory para que devuelva nuestro mock
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
    ) as mock_factory:
        mock_factory.return_value = mock_llm_adapter
        app = create_app()
        yield TestClient(app), mock_llm_adapter


def test_health_endpoint(client):
    """Test: endpoint de health check."""
    test_client, _ = client
    response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_text_response_success(client):
    """Test: generar respuesta de texto exitosamente."""
    from datetime import datetime

    test_client, mock_llm = client

    # Mock del LLM response
    mock_llm.generate_response.return_value = LLMResponse(
        content="¡Hola! ¿Cómo puedo ayudarte?",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=25,
        finish_reason="stop",
        metadata={"completion_tokens": 15, "prompt_tokens": 10},
        created_at=datetime.now(),
    )

    # Request
    payload = {"message": "Hola, ¿cómo estás?"}

    response = test_client.post("/api/v1/chat/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "¡Hola! ¿Cómo puedo ayudarte?"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o-mini"
    assert data["tokens_used"] == 25
    assert data["finish_reason"] == "stop"


def test_generate_text_response_with_system_prompt(client):
    """Test: generar respuesta con system prompt."""
    from datetime import datetime

    test_client, mock_llm = client

    mock_llm.generate_response.return_value = LLMResponse(
        content="Hello world",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=10,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    payload = {
        "message": "Traduce: Hola mundo",
        "system_prompt": "Eres un traductor profesional",
        "temperature": 0.3,
        "max_tokens": 500,
    }

    response = test_client.post("/api/v1/chat/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello world"

    # Verificar que se llamó con los parámetros correctos
    mock_llm.generate_response.assert_called_once()
    call_kwargs = mock_llm.generate_response.call_args.kwargs
    assert call_kwargs["system_prompt"] == "Eres un traductor profesional"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["max_tokens"] == 500


def test_generate_text_response_validation_error(client):
    """Test: validación de request inválido."""
    test_client, _ = client

    # Mensaje vacío
    payload = {"message": ""}
    response = test_client.post("/api/v1/chat/generate", json=payload)
    assert response.status_code == 422

    # Temperature fuera de rango
    payload = {"message": "Test", "temperature": 3.0}
    response = test_client.post("/api/v1/chat/generate", json=payload)
    assert response.status_code == 422


def test_generate_text_response_ai_provider_error(client):
    """Test: manejo de error del proveedor de IA."""
    from src.domain.exceptions.ai_exceptions import AIProviderError

    test_client, mock_llm = client

    # Simular error del proveedor
    mock_llm.generate_response.side_effect = AIProviderError("API key inválida", provider="openai")

    payload = {"message": "Test"}
    response = test_client.post("/api/v1/chat/generate", json=payload)

    assert response.status_code == 500
    assert "Error al generar respuesta" in response.json()["detail"]
