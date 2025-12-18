"""Tests de integración para el endpoint de creación de voz (TTS)."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.models.audio import AudioOutput
from src.interfaces.api.main import create_app


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False

@pytest.fixture
def mock_tts_adapter():
    """Crea un mock del TTS adapter."""
    tts = MagicMock()
    tts.synthesize_speech = AsyncMock()
    tts.get_provider_name = MagicMock(return_value="openai")
    return tts


@pytest.fixture
def mock_storage_adapter():
    """Crea un mock del storage adapter."""
    from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter

    adapter = MagicMock()
    adapter.save_file = AsyncMock(return_value="audio/tts/test_audio.mp3")
    adapter.get_public_url = MagicMock(return_value="https://example.com/audio/tts/test_audio.mp3")
    adapter.__class__ = Boto3StorageAdapter
    return adapter


@pytest.fixture
def client(mock_tts_adapter, mock_storage_adapter):
    """Crea un cliente de prueba con TTS mockeado."""
    from src.application.use_cases.generate_audio_response_use_case import (
        GenerateAudioResponseUseCase,
    )
    from src.config import settings

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Crear un use case real pero con TTS mockeado
    real_use_case = GenerateAudioResponseUseCase(tts=mock_tts_adapter)

    # Patch las dependencias en el container
    with (
        patch(
            "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_tts_adapter"
        ) as mock_tts_factory,
        patch(
            "src.infrastructure.adapters.storage.factory.StorageProviderFactory.create_storage_adapter"
        ) as mock_storage_factory,
    ):
        mock_tts_factory.return_value = mock_tts_adapter
        mock_storage_factory.return_value = mock_storage_adapter
        with patch(
            "src.container.Container.generate_audio_response_use_case"
        ) as mock_use_case_provider:
            mock_use_case_provider.return_value = real_use_case
            app = create_app()
            yield TestClient(app), mock_tts_adapter

    # Restaurar el API key original
    settings.api_key = original_api_key


def test_create_voice_success(client):
    """Test: generar audio exitosamente."""
    test_client, mock_tts = client

    # Mock del resultado de TTS
    mock_audio_output = AudioOutput(
        audio_data=b"fake audio binary data",
        format="mp3",
        duration_seconds=2.5,
        voice_used="alloy",
        provider="openai",
        metadata={"model": "tts-1"},
    )
    mock_tts.synthesize_speech.return_value = mock_audio_output

    # Request
    payload = {
        "text": "Hello, this is a test",
        "voice": "alloy",
        "audio_format": "mp3",
        "speed": 1.0,
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    # Verificar que la respuesta es JSON
    response_data = response.json()
    assert "url" in response_data
    assert "key" in response_data
    assert "duration_seconds" in response_data
    assert "voice_used" in response_data
    assert "provider" in response_data
    assert "format" in response_data
    assert "filename" in response_data

    # Verificar valores en la respuesta
    assert response_data["duration_seconds"] == 2.5
    assert response_data["voice_used"] == "alloy"
    assert response_data["provider"] == "openai"
    assert response_data["format"] == "mp3"
    assert is_valid_uuid(response_data["filename"]) is True

    # Verificar que se llamó al TTS
    mock_tts.synthesize_speech.assert_called_once()
    call_kwargs = mock_tts.synthesize_speech.call_args.kwargs
    assert call_kwargs["text"] == "Hello, this is a test"
    assert call_kwargs["voice"] == "alloy"
    assert call_kwargs["audio_format"] == "mp3"
    assert call_kwargs["speed"] == 1.0


def test_create_voice_with_defaults(client):
    """Test: generar audio con valores por defecto."""
    test_client, mock_tts = client

    mock_audio_output = AudioOutput(
        audio_data=b"fake audio",
        format="mp3",
        duration_seconds=1.0,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )
    mock_tts.synthesize_speech.return_value = mock_audio_output

    payload = {
        "text": "Test text",
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 200
    # Verificar que se usaron los valores por defecto
    call_kwargs = mock_tts.synthesize_speech.call_args.kwargs
    assert call_kwargs["voice"] == "default"
    assert call_kwargs["audio_format"] == "mp3"
    assert call_kwargs["speed"] == 1.0


def test_create_voice_different_formats(client):
    """Test: generar audio en diferentes formatos."""
    test_client, mock_tts = client

    formats = ["mp3", "ogg", "wav"]

    for audio_format in formats:
        mock_audio_output = AudioOutput(
            audio_data=b"fake audio",
            format=audio_format,
            duration_seconds=1.0,
            voice_used="alloy",
            provider="openai",
            metadata={},
        )
        mock_tts.synthesize_speech.return_value = mock_audio_output

        payload = {
            "text": "Test",
            "audio_format": audio_format,
        }

        response = test_client.post(
            "/api/v1/audio/create_voice",
            json=payload,
            headers={"X-API-Key": "valid_key"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        response_data = response.json()
        assert response_data["format"] == audio_format
        mock_tts.reset_mock()


def test_create_voice_missing_api_key(client):
    """Test: error cuando falta API key."""
    test_client, _ = client

    payload = {
        "text": "Test",
    }

    response = test_client.post("/api/v1/audio/create_voice", json=payload)

    assert response.status_code == 422  # FastAPI valida headers requeridos


def test_create_voice_invalid_api_key(client):
    """Test: error con API key inválida."""
    test_client, _ = client
    from src.config import settings

    payload = {
        "text": "Test",
    }

    # Cambiar temporalmente el API key a uno diferente
    original_api_key = settings.api_key
    settings.api_key = "different_key"

    try:
        response = test_client.post(
            "/api/v1/audio/create_voice",
            json=payload,
            headers={"X-API-Key": "invalid_key"},
        )

        assert response.status_code == 401
    finally:
        # Restaurar el API key original
        settings.api_key = original_api_key


def test_create_voice_validation_error_empty_text(client):
    """Test: validación de texto vacío."""
    test_client, _ = client

    payload = {
        "text": "",  # Texto vacío
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 422


def test_create_voice_validation_error_invalid_format(client):
    """Test: validación de formato inválido."""
    test_client, _ = client

    payload = {
        "text": "Test",
        "audio_format": "invalid_format",
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 422


def test_create_voice_validation_error_invalid_speed(client):
    """Test: validación de velocidad inválida."""
    test_client, _ = client

    payload = {
        "text": "Test",
        "speed": 5.0,  # Velocidad fuera de rango
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 422


def test_create_voice_tts_error(client):
    """Test: manejo de error del TTS."""
    test_client, mock_tts = client
    from src.domain.exceptions.ai_exceptions import AIProviderError

    # Simular error del TTS
    mock_tts.synthesize_speech.side_effect = AIProviderError("Error en TTS", provider="openai")

    payload = {
        "text": "Test",
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 500
    assert "Error al generar audio" in response.json()["detail"]


def test_create_voice_response_headers(client):
    """Test: verificar headers de respuesta."""
    test_client, mock_tts = client

    mock_audio_output = AudioOutput(
        audio_data=b"fake audio",
        format="mp3",
        duration_seconds=3.5,
        voice_used="nova",
        provider="openai",
        metadata={},
    )
    mock_tts.synthesize_speech.return_value = mock_audio_output

    payload = {
        "text": "Test",
    }

    response = test_client.post(
        "/api/v1/audio/create_voice",
        json=payload,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    response_data = response.json()
    assert response_data["duration_seconds"] == 3.5
    assert response_data["voice_used"] == "nova"
    assert response_data["provider"] == "openai"
    assert response_data["format"] == "mp3"
    # Verificar que la URL y key están presentes
    assert "url" in response_data
    assert "key" in response_data
    assert response_data["url"].startswith("http")
    assert "audio" in response_data["key"]
