"""Tests de integración para el endpoint de traducción."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

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

    from src.application.use_cases.batch_translate_use_case import BatchTranslateUseCase
    from src.application.use_cases.translate_message_use_case import TranslateMessageUseCase
    from src.config import settings
    from src.container import Container
    from src.interfaces.api.auth import verify_token

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "test-api-key"

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
            return "test-api-key"

        app.dependency_overrides[verify_token] = mock_verify_token

        # Hacer override directo de las dependencias Provide del endpoint
        # Esto es necesario porque Provide se resuelve cuando se importa el módulo
        batch_dep = Provide[Container.batch_translate_use_case]
        message_dep = Provide[Container.translate_message_use_case]

        def override_batch():
            return real_batch_use_case

        def override_message():
            return real_message_use_case

        app.dependency_overrides[batch_dep] = override_batch
        app.dependency_overrides[message_dep] = override_message

        yield TestClient(app), mock_llm_adapter, mock_prompt_manager, app

        # Limpiar overrides
        app.dependency_overrides.clear()

    # Restaurar el API key original
    settings.api_key = original_api_key


@pytest.fixture
def api_key():
    """API key para las pruebas."""
    from src.config import settings

    # Usar una API key de prueba para los tests
    original_api_key = settings.api_key
    settings.api_key = "test-api-key"
    yield "test-api-key"
    # Restaurar el API key original
    settings.api_key = original_api_key


@pytest.mark.integration
def test_translate_message_text_integration(client, api_key):
    """Test de integración: traducir un mensaje de texto simple."""
    test_client, mock_llm, mock_pm, _ = client

    # Arrange
    request_data = {
        "message_text": "Hello, how are you?",
        "target_language": "Spanish",
    }

    # Mock de los prompts
    mock_pm.render.side_effect = [
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
    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    response = test_client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": api_key},
        json=request_data,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "translation" in data
    assert isinstance(data["translation"], dict)
    assert "id" in data["translation"]
    assert "translation" in data["translation"]
    assert len(data["translation"]["translation"]) > 0
    assert "provider" in data
    assert "model" in data
    mock_llm.generate_response.assert_called_once()


@pytest.mark.integration
def test_translate_batch_data_integration(client, api_key):
    """Test de integración: traducir datos batch (array JSON)."""
    test_client, mock_llm, mock_pm, _ = client

    # Arrange
    request_data = {
        "data": [
            {"id": "1", "word": "Hello"},
            {"id": "2", "word": "World"},
            {"id": "3", "word": "Good morning"},
        ],
        "target_language": "Spanish",
    }

    # Mock de los prompts
    mock_pm.render.side_effect = [
        {"properties": {"translations": {"type": "array"}}},  # create_response_schema
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
    ]

    # Mock de la respuesta del LLM
    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hola"}, {"id": "2", "translation": "Mundo"}, {"id": "3", "translation": "Buenos días"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )
    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    response = test_client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": api_key},
        json=request_data,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert isinstance(data["translations"], list)
    assert len(data["translations"]) == 3

    # Verificar estructura de cada traducción
    for translation in data["translations"]:
        assert "id" in translation
        assert "translation" in translation
        assert isinstance(translation["id"], str)
        assert isinstance(translation["translation"], str)

    assert "provider" in data
    assert "model" in data
    mock_llm.generate_response.assert_called_once()


@pytest.mark.integration
def test_translate_with_native_language(client, api_key):
    """Test de integración: traducir con idioma nativo especificado."""
    test_client, mock_llm, mock_pm, _ = client

    # Arrange
    request_data = {
        "message_text": "Bonjour",
        "target_language": "English",
        "native_language": "French",
    }

    # Mock de los prompts
    mock_pm.render.side_effect = [
        "Translate system prompt",  # create_system
        "User prompt",  # create_user
        {"properties": {"translations": {"type": "array"}}},  # create_response_schema
    ]

    # Mock de la respuesta del LLM
    expected_llm_response = LLMResponse(
        content='{"translations": [{"id": "1", "translation": "Hello"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=30,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )
    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    response = test_client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": api_key},
        json=request_data,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "translation" in data
    assert isinstance(data["translation"], dict)
    assert "id" in data["translation"]
    assert "translation" in data["translation"]
    mock_llm.generate_response.assert_called_once()


@pytest.mark.integration
def test_translate_mixed_payload_validation(client, api_key):
    """Test de integración: validación de payload mixto (no debe permitir ambos)."""
    test_client, _, _, _ = client

    # Arrange - Intentar enviar ambos message_text y data
    request_data = {
        "message_text": "Hello",
        "data": [{"id": "1", "word": "Hello"}],
        "target_language": "Spanish",
    }

    # Act
    response = test_client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": api_key},
        json=request_data,
    )

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_translate_missing_required_fields(client, api_key):
    """Test de integración: error cuando faltan campos requeridos."""
    test_client, _, _, _ = client

    # Arrange - Sin message_text ni data
    request_data = {
        "target_language": "Spanish",
    }

    # Act
    response = test_client.post(
        "/api/v1/translation/translations",
        headers={"X-API-Key": api_key},
        json=request_data,
    )

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.integration
def test_translate_invalid_api_key(client):
    """Test de integración: error con API key inválida."""
    from src.interfaces.api.auth import verify_token

    test_client, _, _, app = client

    # Override el verify_token para este test específico para que rechace la API key inválida
    async def mock_verify_token_invalid(api_key: str | None = None):
        from fastapi import HTTPException, status

        if api_key != "test-api-key":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key inválida o no proporcionada",
                headers={"WWW-Authenticate": "X-API-Key"},
            )
        return api_key

    # Hacer override del verify_token para este test
    app.dependency_overrides[verify_token] = mock_verify_token_invalid

    try:
        # Arrange
        request_data = {
            "message_text": "Hello",
            "target_language": "Spanish",
        }

        # Act
        response = test_client.post(
            "/api/v1/translation/translations",
            headers={"X-API-Key": "invalid-key"},
            json=request_data,
        )

        # Assert
        assert response.status_code == 401  # Unauthorized
    finally:
        # Restaurar el override original del fixture
        async def mock_verify_token(api_key: str | None = None):
            return "test-api-key"

        app.dependency_overrides[verify_token] = mock_verify_token
