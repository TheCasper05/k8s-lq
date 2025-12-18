"""Tests unitarios para el adaptador Eleven Labs STT."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.infrastructure.adapters.ai.elevenlabs.elevenlabs_stt_adapter import ElevenLabsSTTAdapter


@pytest.fixture
def adapter():
    """Crea una instancia del adaptador."""
    return ElevenLabsSTTAdapter(api_key="test_key", model="scribe-v2-realtime", language="en")


class TestElevenLabsSTTAdapter:
    """Tests para ElevenLabsSTTAdapter."""

    def test_init_with_defaults(self):
        """Test: inicialización con valores por defecto."""
        adapter = ElevenLabsSTTAdapter(api_key="test_key")
        assert adapter.api_key == "test_key"
        assert adapter.model == "scribe-v2-realtime"
        assert adapter.default_language == "en"
        assert adapter.provider_name == "elevenlabs"
        assert adapter.base_url == "https://api.elevenlabs.io/v1"

    def test_init_with_custom_params(self):
        """Test: inicialización con parámetros personalizados."""
        adapter = ElevenLabsSTTAdapter(api_key="custom_key", model="custom-model", language="es")
        assert adapter.api_key == "custom_key"
        assert adapter.model == "custom-model"
        assert adapter.default_language == "es"

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_bytes(self, adapter):
        """Test: transcribir audio desde bytes."""
        # Arrange
        audio_data = b"fake_audio_data"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "text": "Hello world",
            "language": "en",
            "confidence": 0.95,
            "duration": 2.5,
            "detected_language": "en",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            result = await adapter.transcribe_audio(audio=audio_data, language="en")

            # Assert
            assert result.text == "Hello world"
            assert result.language == "en"
            assert result.confidence == 0.95
            assert result.duration_seconds == 2.5
            assert result.provider == "elevenlabs"
            assert result.metadata["model"] == "scribe-v2-realtime"
            assert result.metadata["detected_language"] == "en"

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert "files" in call_kwargs.kwargs
            assert "data" in call_kwargs.kwargs
            assert call_kwargs.kwargs["data"]["model"] == "scribe-v2-realtime"
            assert call_kwargs.kwargs["data"]["language"] == "en"

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_path(self, adapter):
        """Test: transcribir audio desde Path."""
        # Arrange
        audio_path = Path("/tmp/test_audio.mp3")
        audio_data = b"fake_audio_data"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "text": "Test transcription",
            "language": "es",
            "duration": 1.0,
        }
        mock_response.raise_for_status = MagicMock()

        with (
            patch("httpx.AsyncClient") as mock_client_class,
            patch.object(Path, "read_bytes", return_value=audio_data),
        ):
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            result = await adapter.transcribe_audio(audio=audio_path)

            # Assert
            assert result.text == "Test transcription"
            assert result.language == "es"  # Usa default_language cuando no se especifica

    @pytest.mark.asyncio
    async def test_transcribe_audio_uses_default_language_when_none(self, adapter):
        """Test: usar idioma por defecto cuando language es None."""
        # Arrange
        audio_data = b"fake_audio_data"
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Test", "language": "en"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            await adapter.transcribe_audio(audio=audio_data, language=None)

            # Assert
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["data"]["language"] == "en"  # default_language

    @pytest.mark.asyncio
    async def test_transcribe_audio_handles_http_error(self, adapter):
        """Test: manejar error HTTP de Eleven Labs."""
        # Arrange
        audio_data = b"fake_audio_data"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        http_error = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(side_effect=http_error)
            mock_client_class.return_value = mock_client

            # Act & Assert
            with pytest.raises(AIProviderError) as exc_info:
                await adapter.transcribe_audio(audio=audio_data)

            assert "Error HTTP de Eleven Labs STT" in str(exc_info.value)
            assert exc_info.value.provider == "elevenlabs"
            assert exc_info.value.original_error == http_error

    @pytest.mark.asyncio
    async def test_transcribe_audio_handles_general_error(self, adapter):
        """Test: manejar error general."""
        # Arrange
        audio_data = b"fake_audio_data"
        general_error = Exception("Network error")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(side_effect=general_error)
            mock_client_class.return_value = mock_client

            # Act & Assert
            with pytest.raises(AIProviderError) as exc_info:
                await adapter.transcribe_audio(audio=audio_data)

            assert "Error en Eleven Labs STT" in str(exc_info.value)
            assert exc_info.value.provider == "elevenlabs"
            assert exc_info.value.original_error == general_error

    @pytest.mark.asyncio
    async def test_translate_audio_calls_transcribe(self, adapter):
        """Test: translate_audio llama a transcribe_audio."""
        # Arrange
        audio_data = b"fake_audio_data"
        mock_response = MagicMock()
        mock_response.json.return_value = {"text": "Translated text", "language": "en"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            result = await adapter.translate_audio(audio=audio_data, target_language="es")

            # Assert
            assert result.text == "Translated text"
            # translate_audio llama a transcribe_audio con language=None
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["data"]["language"] == "en"  # default_language

    def test_get_supported_formats(self, adapter):
        """Test: obtener formatos soportados."""
        formats = adapter.get_supported_formats()
        assert isinstance(formats, list)
        assert "mp3" in formats
        assert "wav" in formats
        assert "flac" in formats
        assert "ogg" in formats
        assert "m4a" in formats

    def test_get_provider_name(self, adapter):
        """Test: obtener nombre del proveedor."""
        assert adapter.get_provider_name() == "elevenlabs"

    def test_get_model_info(self, adapter):
        """Test: obtener información del modelo."""
        info = adapter.get_model_info()
        assert info["provider"] == "elevenlabs"
        assert info["model"] == "scribe-v2-realtime"
        assert "capabilities" in info
        assert "realtime_transcription" in info["capabilities"]
        assert "multilingual" in info["capabilities"]
        assert "supported_formats" in info
