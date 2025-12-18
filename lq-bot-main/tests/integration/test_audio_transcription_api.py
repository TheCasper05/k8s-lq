"""Tests de integración para el endpoint de transcripción de audio."""

from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.domain.models.audio import TranscriptionResult
from src.interfaces.api.main import create_app


@pytest.fixture
def mock_stt_adapter():
    """Crea un mock del STT adapter."""
    stt = MagicMock()
    stt.transcribe_audio = AsyncMock()
    stt.model = "whisper-1"
    stt.get_provider_name = MagicMock(return_value="openai")
    return stt


@pytest.fixture
def mock_storage_adapter():
    """Crea un mock del storage adapter."""
    storage = MagicMock()
    storage.get_file = AsyncMock(return_value=b"audio data from storage")
    return storage


@pytest.fixture
def client(mock_stt_adapter, mock_storage_adapter):
    """Crea un cliente de prueba con STT y storage mockeados."""
    from src.application.use_cases.generate_transcription_use_case import (
        GenerateTranscriptionUseCase,
    )
    from src.config import settings

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Crear un use case real pero con STT mockeado
    real_use_case = GenerateTranscriptionUseCase(stt=mock_stt_adapter)

    # Patch las dependencias en el container
    # Hacer patch del factory para que retorne el mock del STT
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_stt_adapter"
    ) as mock_stt_factory:
        mock_stt_factory.return_value = mock_stt_adapter
        # Hacer patch del factory de storage
        with patch(
            "src.infrastructure.adapters.storage.factory.StorageProviderFactory.create_storage_adapter"
        ) as mock_storage_factory:
            mock_storage_factory.return_value = mock_storage_adapter
            # Hacer patch del provider del use case para que retorne nuestro use case con el mock
            with patch(
                "src.container.Container.generate_transcription_use_case"
            ) as mock_use_case_provider:
                mock_use_case_provider.return_value = real_use_case
                app = create_app()
                yield TestClient(app), mock_stt_adapter, mock_storage_adapter

    # Restaurar el API key original
    settings.api_key = original_api_key


def test_transcription_with_file_success(client):
    """Test: transcribir audio desde archivo subido exitosamente."""
    test_client, mock_stt, _ = client

    # Mock del resultado de transcripción
    mock_result = TranscriptionResult(
        text="Hello, this is a test transcription",
        language="en",
        confidence=0.95,
        provider="openai",
        duration_seconds=2.5,
        metadata={},
    )
    mock_stt.transcribe_audio.return_value = mock_result

    # Crear archivo de audio simulado
    audio_data = b"fake audio binary data"
    files = {"file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")}
    data = {"language": "en"}

    response = test_client.post(
        "/api/v1/audio/transcription",
        files=files,
        data=data,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["transcription"] == "Hello, this is a test transcription"
    assert response_data["provider"] == "openai"
    assert response_data["model"] == "whisper-1"

    # Verificar que se llamó al STT
    mock_stt.transcribe_audio.assert_called_once()
    call_args = mock_stt.transcribe_audio.call_args
    assert call_args.kwargs["language"] == "en"


def test_transcription_with_url_success(client):
    """Test: transcribir audio desde URL exitosamente."""
    test_client, mock_stt, mock_storage = client

    # Mock del resultado de transcripción
    mock_result = TranscriptionResult(
        text="Transcribed from URL",
        language="es",
        confidence=0.92,
        provider="openai",
        duration_seconds=3.0,
        metadata={},
    )
    mock_stt.transcribe_audio.return_value = mock_result

    # URL S3 - enviar como JSON
    s3_url = "https://bucket.s3.amazonaws.com/path/to/audio.mp3"

    data = {
        "url": s3_url,
        "language": "es",
    }

    response = test_client.post(
        "/api/v1/audio/transcription",
        json=data,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["transcription"] == "Transcribed from URL"
    assert response_data["provider"] == "openai"

    # Verificar que se descargó el archivo desde storage
    mock_storage.get_file.assert_called_once_with("path/to/audio.mp3")
    mock_stt.transcribe_audio.assert_called_once()


def test_transcription_with_http_url_success(client):
    """Test: transcribir audio desde URL HTTP exitosamente."""
    test_client, mock_stt, _ = client

    # Mock del resultado de transcripción
    mock_result = TranscriptionResult(
        text="Transcribed from HTTP",
        language="en",
        confidence=0.90,
        provider="openai",
        duration_seconds=1.5,
        metadata={},
    )
    mock_stt.transcribe_audio.return_value = mock_result

    http_url = "https://example.com/audio.mp3"

    data = {
        "url": http_url,
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_response = MagicMock()
        mock_response.content = b"audio from http"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        response = test_client.post(
            "/api/v1/audio/transcription",
            json=data,
            headers={"X-API-Key": "valid_key"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["transcription"] == "Transcribed from HTTP"


def test_transcription_missing_api_key(client):
    """Test: error cuando falta API key."""
    test_client, _, _ = client

    audio_data = b"fake audio"
    files = {"file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")}

    response = test_client.post("/api/v1/audio/transcription", files=files)

    assert response.status_code == 422  # FastAPI valida headers requeridos


def test_transcription_invalid_api_key(client):
    """Test: error con API key inválida."""
    test_client, _, _ = client
    from src.config import settings

    audio_data = b"fake audio"
    files = {"file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")}

    # Cambiar temporalmente el API key a uno diferente
    original_api_key = settings.api_key
    settings.api_key = "different_key"

    try:
        response = test_client.post(
            "/api/v1/audio/transcription",
            files=files,
            headers={"X-API-Key": "invalid_key"},
        )

        assert response.status_code == 401
    finally:
        # Restaurar el API key original
        settings.api_key = original_api_key


def test_transcription_missing_file_and_url(client):
    """Test: error cuando no se proporciona file ni url."""
    test_client, _, _ = client

    # Enviar como JSON vacío
    data = {}

    response = test_client.post(
        "/api/v1/audio/transcription",
        json=data,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 400
    assert "file" in response.json()["detail"].lower() or "url" in response.json()["detail"].lower()


def test_transcription_both_file_and_url(client):
    """Test: error cuando se proporcionan file y url."""
    test_client, _, _ = client

    audio_data = b"fake audio"
    files = {"file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")}
    data = {"url": "https://example.com/audio.mp3"}

    response = test_client.post(
        "/api/v1/audio/transcription",
        files=files,
        data=data,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 400
    assert (
        "ambos" in response.json()["detail"].lower() or "both" in response.json()["detail"].lower()
    )


def test_transcription_stt_error(client):
    """Test: manejo de error del STT."""
    test_client, mock_stt, _ = client
    from src.domain.exceptions.ai_exceptions import AIProviderError

    # Simular error del STT
    mock_stt.transcribe_audio.side_effect = AIProviderError("Error en STT", provider="openai")

    audio_data = b"fake audio"
    files = {"file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")}

    response = test_client.post(
        "/api/v1/audio/transcription",
        files=files,
        headers={"X-API-Key": "valid_key"},
    )

    assert response.status_code == 500
    assert "Error al transcribir" in response.json()["detail"]
