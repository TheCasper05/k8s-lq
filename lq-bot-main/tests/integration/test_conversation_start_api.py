"""Tests de integración para el endpoint de conversation/start."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.models.audio import AudioOutput
from src.domain.models.message import LLMResponse
from src.interfaces.api.main import create_app


@pytest.fixture
def mock_llm_adapter():
    """Crea un mock del LLM adapter."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm


@pytest.fixture
def mock_tts_adapter():
    """Crea un mock del TTS adapter."""
    tts = MagicMock()
    tts.synthesize_speech = AsyncMock()
    return tts


@pytest.fixture
def mock_stt_adapter():
    """Crea un mock del STT adapter."""
    stt = MagicMock()
    stt.transcribe_audio = AsyncMock()
    return stt


@pytest.fixture
def mock_storage_adapter():
    """Crea un mock del storage adapter."""
    from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter

    adapter = MagicMock()
    adapter.save_file = AsyncMock(return_value="conversations/audio/test_audio.mp3")
    adapter.get_public_url = MagicMock(
        return_value="https://example.com/conversations/audio/test_audio.mp3"
    )
    adapter.__class__ = Boto3StorageAdapter
    return adapter


@pytest.fixture
def client(mock_llm_adapter, mock_tts_adapter, mock_stt_adapter, mock_storage_adapter):
    """Crea un cliente de prueba con adaptadores mockeados."""
    from src.application.use_cases.generate_text_response_use_case import (
        GenerateTextResponseUseCase,
    )
    from src.config import settings

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "test-api-key"

    # Crear un use case real pero con LLM mockeado
    real_use_case = GenerateTextResponseUseCase(llm=mock_llm_adapter)

    # Patch el factory de AI ANTES de importar create_app
    with (
        patch(
            "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
        ) as mock_llm_factory,
        patch(
            "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_tts_adapter"
        ) as mock_tts_factory,
        patch(
            "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_stt_adapter"
        ) as mock_stt_factory,
        patch(
            "src.infrastructure.adapters.storage.factory.StorageProviderFactory.create_storage_adapter"
        ) as mock_storage_factory,
    ):
        mock_llm_factory.return_value = mock_llm_adapter
        mock_tts_factory.return_value = mock_tts_adapter
        mock_stt_factory.return_value = mock_stt_adapter
        mock_storage_factory.return_value = mock_storage_adapter

        # Patch las funciones en conversation_service que usan el container
        with patch(
            "src.domain.services.conversation_service.generate_text_response_use_case"
        ) as mock_use_case_func:
            mock_use_case_func.return_value = real_use_case
            app = create_app()
            yield (
                TestClient(app),
                mock_llm_adapter,
                mock_tts_adapter,
                mock_stt_adapter,
            )

    # Restaurar el API key original
    settings.api_key = original_api_key


def test_conversation_start_success(client):
    """Test: iniciar conversación exitosamente."""
    test_client, mock_llm, mock_tts, _ = client

    # Mock del LLM response (usado internamente por process_text_answer)
    mock_llm_response = LLMResponse(
        content="Welcome! Let's start practicing English conversation.",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=30,
        finish_reason="stop",
        response_id="resp_welcome_123",
        metadata={"completion_tokens": 20, "prompt_tokens": 10},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_llm_response

    # Mock del TTS response
    audio_bytes = b"fake_audio_data_for_welcome"
    mock_audio_output = AudioOutput(
        audio_data=audio_bytes,
        format="mp3",
        duration_seconds=2.5,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )

    mock_tts.synthesize_speech.return_value = mock_audio_output

    # Request payload (igual que text_answer pero sin message y response_id)
    payload = {
        "scenario_type": "roleplay",
        "language": "English",
        "theme": "Restaurant conversation",
        "assistant_role": "waiter",
        "user_role": "customer",
        "potential_directions": "ordering food, asking about menu",
        "setting": "Italian restaurant",
        "example": "Customer: I'd like pizza. Waiter: What size?",
        "additional_data": "Use polite language",
        "practice_topic": "restaurant vocabulary",
    }

    # Headers con API key
    headers = {"X-API-Key": "test-api-key"}

    # Act
    response = test_client.post("/api/v1/conversation/start", json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    # Verificar que la respuesta es JSON
    response_data = response.json()
    assert "conversation_id" in response_data
    assert "response_id" in response_data
    assert "audio_url" in response_data
    assert "audio_key" in response_data
    assert "audio_duration" in response_data
    assert "voice_used" in response_data
    assert "provider" in response_data
    assert "audio_format" in response_data
    assert "filename" in response_data

    # Verificar valores en la respuesta
    assert response_data["response_id"] == "resp_welcome_123"
    conversation_id = response_data["conversation_id"]
    assert len(conversation_id) == 36  # UUID tiene 36 caracteres

    # Verificar que la URL y key están presentes
    assert response_data["audio_url"].startswith("http")
    assert "audio" in response_data["audio_key"]

    # Verificar que se llamó al TTS con el mensaje correcto
    mock_tts.synthesize_speech.assert_called_once()
    call_args = mock_tts.synthesize_speech.call_args
    assert call_args.kwargs["text"] == "Welcome! Let's start practicing English conversation."
    assert call_args.kwargs["audio_format"] == "mp3"


def test_conversation_start_missing_api_key(client):
    """Test: verificar que se requiere API key."""
    test_client, _, _, _ = client

    payload = {
        "scenario_type": "roleplay",
        "language": "English",
    }

    # Sin headers
    response = test_client.post("/api/v1/conversation/start", json=payload)

    assert response.status_code == 422  # FastAPI valida headers requeridos


def test_conversation_start_invalid_api_key(client):
    """Test: verificar que se rechaza API key inválida."""
    test_client, _, _, _ = client

    payload = {
        "scenario_type": "roleplay",
        "language": "English",
    }

    # Headers con API key inválida (diferente a "test-api-key" configurada en el fixture)
    headers = {"X-API-Key": "invalid-key"}

    response = test_client.post("/api/v1/conversation/start", json=payload, headers=headers)

    assert response.status_code == 401
    # Cuando hay error, FastAPI devuelve JSON
    assert "API key inválida" in response.json()["detail"]


def test_conversation_start_missing_required_fields(client):
    """Test: verificar validación de campos requeridos."""
    test_client, _, _, _ = client

    headers = {"X-API-Key": "test-api-key"}

    # Payload sin scenario_type
    payload = {
        "language": "English",
    }

    response = test_client.post("/api/v1/conversation/start", json=payload, headers=headers)

    assert response.status_code == 422  # Error de validación


def test_conversation_start_different_languages(client):
    """Test: verificar que funciona con diferentes idiomas."""
    test_client, mock_llm, mock_tts, _ = client

    mock_llm_response = LLMResponse(
        content="¡Bienvenido! Empecemos a practicar español.",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=25,
        finish_reason="stop",
        response_id="resp_spanish_123",
        metadata={"completion_tokens": 15, "prompt_tokens": 10},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = mock_llm_response

    audio_bytes = b"spanish_audio_data"
    mock_audio_output = AudioOutput(
        audio_data=audio_bytes,
        format="mp3",
        duration_seconds=2.0,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )

    mock_tts.synthesize_speech.return_value = mock_audio_output

    payload = {
        "scenario_type": "roleplay",
        "language": "Spanish",
        "theme": "Restaurant",
    }

    headers = {"X-API-Key": "test-api-key"}

    response = test_client.post("/api/v1/conversation/start", json=payload, headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["response_id"] == "resp_spanish_123"
    assert response_data["audio_url"].startswith("http")
    assert "audio" in response_data["audio_key"]

    # Verificar que se llamó al TTS
    mock_tts.synthesize_speech.assert_called_once()


def test_conversation_start_ai_error(client):
    """Test: manejo de error del proveedor AI."""
    from src.domain.exceptions.ai_exceptions import AIProviderError

    test_client, mock_llm, _, _ = client

    # Simular error del LLM
    mock_llm.generate_response.side_effect = AIProviderError("API key inválida", provider="openai")

    payload = {
        "scenario_type": "roleplay",
        "language": "English",
    }

    headers = {"X-API-Key": "test-api-key"}

    response = test_client.post("/api/v1/conversation/start", json=payload, headers=headers)

    assert response.status_code == 500
    assert "Error al iniciar conversación" in response.json()["detail"]
