"""Tests unitarios para el endpoint de traducción."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.batch_translate_use_case import BatchTranslateUseCase
from src.application.use_cases.translate_message_use_case import TranslateMessageUseCase

# Importar Container para poder hacer patch antes de que se importe translation_routes
from src.container import Container
from src.domain.models.message import LLMResponse


@pytest.fixture
def mock_llm_adapter():
    """Crea un mock del LLM adapter."""
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
def client(mock_llm_adapter, mock_prompt_manager):
    """Crea un cliente de prueba con LLM y PromptManager mockeados."""
    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.interfaces.api.auth import verify_token

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Crear casos de uso reales pero con LLM y PromptManager mockeados
    real_batch_use_case = BatchTranslateUseCase(
        llm=mock_llm_adapter, prompt_manager=mock_prompt_manager
    )
    real_message_use_case = TranslateMessageUseCase(
        llm=mock_llm_adapter, prompt_manager=mock_prompt_manager
    )

    # Patch el factory de LLM ANTES de importar create_app (esto evita crear un LLM real)
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
    ) as mock_llm_factory:
        mock_llm_factory.return_value = mock_llm_adapter

        from src.interfaces.api.main import create_app

        app = create_app()

        # Override de dependencias de FastAPI
        async def mock_verify_token(api_key: str | None = None):
            return "valid_key"

        app.dependency_overrides[verify_token] = mock_verify_token

        # Hacer override directo de las dependencias Provide del endpoint
        batch_dep = Provide[Container.batch_translate_use_case]
        message_dep = Provide[Container.translate_message_use_case]

        def override_batch():
            return real_batch_use_case

        def override_message():
            return real_message_use_case

        app.dependency_overrides[batch_dep] = override_batch
        app.dependency_overrides[message_dep] = override_message

        client_instance = TestClient(app)
        # Asignar los mocks como atributos para acceso en los tests
        client_instance._mock_llm = mock_llm_adapter
        client_instance._mock_prompt_manager = mock_prompt_manager

        yield client_instance

        # Limpiar overrides
        app.dependency_overrides.clear()

    # Restaurar el API key original
    settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_translate_message_text(client):
    """Test: traducir un mensaje de texto simple."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
        {"properties": {"translations": {"type": "array"}}},  # create_response_schema
    ]

    # Mock de la respuesta del LLM
    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola, ¿cómo estás?"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )
    mock_llm_adapter.generate_response.return_value = expected_llm_response

    # Act
    response = client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": "valid_key"},
        json={
            "message_text": "Hello, how are you?",
            "target_language": "Spanish",
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["translation"], dict)
    assert data["translation"]["id"] == "1"
    assert data["translation"]["translation"] == "Hola, ¿cómo estás?"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o-mini"

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_translate_batch_data(client):
    """Test: traducir datos batch (array JSON)."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        {"properties": {"translations": {"type": "array"}}},  # create_response_schema
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
    ]

    # Mock de la respuesta del LLM
    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola"}, {"id": "2", "translation": "Mundo"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )
    mock_llm_adapter.generate_response.return_value = expected_llm_response

    # Act
    response = client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": "valid_key"},
        json={
            "data": [{"id": "1", "word": "Hello"}, {"id": "2", "word": "World"}],
            "target_language": "Spanish",
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert len(data["translations"]) == 2
    assert data["translations"][0]["id"] == "1"
    assert data["translations"][0]["translation"] == "Hola"

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_translate_missing_input(client):
    """Test: error cuando no se proporciona message_text ni data."""
    # Act
    response = client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": "valid_key"},
        json={
            "target_language": "Spanish",
        },
    )

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_translate_both_inputs(client):
    """Test: error cuando se proporcionan ambos message_text y data."""
    # Act
    response = client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": "valid_key"},
        json={
            "message_text": "Hello",
            "data": [{"id": "1", "word": "Hello"}],
            "target_language": "Spanish",
        },
    )

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_translate_invalid_api_key():
    """Test: error cuando la API key es inválida."""
    from unittest.mock import AsyncMock, MagicMock, patch

    from fastapi import HTTPException

    from src.interfaces.api.auth import verify_token
    from src.interfaces.api.main import create_app

    # Crear mocks del LLM y PromptManager
    mock_llm_adapter = MagicMock()
    mock_llm_adapter.generate_response = AsyncMock()
    mock_llm_adapter.get_provider_name = MagicMock(return_value="openai")
    mock_llm_adapter.get_model_info = MagicMock(return_value={"name": "gpt-4o-mini"})

    mock_prompt_manager = MagicMock()
    mock_prompt_manager.render = MagicMock()

    # Crear casos de uso reales pero con LLM y PromptManager mockeados
    real_batch_use_case = BatchTranslateUseCase(
        llm=mock_llm_adapter, prompt_manager=mock_prompt_manager
    )
    real_message_use_case = TranslateMessageUseCase(
        llm=mock_llm_adapter, prompt_manager=mock_prompt_manager
    )

    # Patch el factory de LLM ANTES de importar create_app
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
    ) as mock_llm_factory:
        mock_llm_factory.return_value = mock_llm_adapter

        app = create_app()

        # Override para simular API key inválida
        async def mock_verify_token_invalid(api_key: str | None = None):
            raise HTTPException(status_code=401, detail="Invalid API key")

        app.dependency_overrides[verify_token] = mock_verify_token_invalid

        # Override de los use cases
        from dependency_injector.wiring import Provide

        from src.container import Container

        batch_dep = Provide[Container.batch_translate_use_case]
        message_dep = Provide[Container.translate_message_use_case]

        app.dependency_overrides[batch_dep] = lambda: real_batch_use_case
        app.dependency_overrides[message_dep] = lambda: real_message_use_case

        client = TestClient(app)

        # Act
        response = client.post(
            "/api/v1/translation/translations",
            headers={"X-API-Key": "invalid_key"},
            json={
                "message_text": "Hello",
                "target_language": "Spanish",
            },
        )

        # Assert
        assert response.status_code == 401

        # Limpiar overrides
        app.dependency_overrides.clear()
