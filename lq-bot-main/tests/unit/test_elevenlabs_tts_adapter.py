"""Tests unitarios para el adaptador Eleven Labs TTS."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.infrastructure.adapters.ai.elevenlabs.elevenlabs_tts_adapter import ElevenLabsTTSAdapter


@pytest.fixture
def adapter():
    """Crea una instancia del adaptador."""
    return ElevenLabsTTSAdapter(
        api_key="test_key", model="eleven_multilingual_v2", voice_id="test_voice_id"
    )


class TestElevenLabsTTSAdapter:
    """Tests para ElevenLabsTTSAdapter."""

    def test_init_with_defaults(self):
        """Test: inicialización con valores por defecto."""
        adapter = ElevenLabsTTSAdapter(api_key="test_key")
        assert adapter.api_key == "test_key"
        assert adapter.model == "eleven_multilingual_v2"
        assert adapter.default_voice_id == "21m00Tcm4TlvDq8ikWAM"  # Rachel default
        assert adapter.provider_name == "elevenlabs"
        assert adapter.base_url == "https://api.elevenlabs.io/v1"

    def test_init_with_custom_params(self):
        """Test: inicialización con parámetros personalizados."""
        adapter = ElevenLabsTTSAdapter(
            api_key="custom_key", model="custom-model", voice_id="custom_voice"
        )
        assert adapter.api_key == "custom_key"
        assert adapter.model == "custom-model"
        assert adapter.default_voice_id == "custom_voice"

    @pytest.mark.asyncio
    async def test_synthesize_speech_with_default_voice(self, adapter):
        """Test: sintetizar audio con voz por defecto."""
        # Arrange
        text = "Hello world"
        audio_data = b"fake_audio_binary_data"
        mock_response = MagicMock()
        mock_response.content = audio_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            result = await adapter.synthesize_speech(text=text, voice="default")

            # Assert
            assert result.audio_data == audio_data
            assert result.format == "mp3"
            assert result.voice_used == adapter.default_voice_id
            assert result.provider == "elevenlabs"
            assert result.metadata["model"] == "eleven_multilingual_v2"
            assert result.metadata["text_length"] == len(text)

            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args
            assert call_kwargs.kwargs["json"]["text"] == text
            assert call_kwargs.kwargs["json"]["model_id"] == adapter.model
            assert "voice_settings" in call_kwargs.kwargs["json"]
            assert call_kwargs.kwargs["params"]["output_format"] == "mp3_44100_128"

    @pytest.mark.asyncio
    async def test_synthesize_speech_with_custom_voice(self, adapter):
        """Test: sintetizar audio con voz personalizada."""
        # Arrange
        text = "Test text"
        custom_voice = "custom_voice_id"
        audio_data = b"audio_data"
        mock_response = MagicMock()
        mock_response.content = audio_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            result = await adapter.synthesize_speech(text=text, voice=custom_voice)

            # Assert
            assert result.voice_used == custom_voice
            call_kwargs = mock_client.post.call_args
            assert custom_voice in call_kwargs.args[0]  # URL contiene voice_id

    @pytest.mark.asyncio
    async def test_synthesize_speech_with_custom_settings(self, adapter):
        """Test: sintetizar audio con configuraciones personalizadas."""
        # Arrange
        text = "Test"
        audio_data = b"audio"
        mock_response = MagicMock()
        mock_response.content = audio_data
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            await adapter.synthesize_speech(
                text=text,
                stability=0.8,
                similarity_boost=0.9,
                style=0.5,
                use_speaker_boost=True,
            )

            # Assert
            call_kwargs = mock_client.post.call_args
            voice_settings = call_kwargs.kwargs["json"]["voice_settings"]
            assert voice_settings["stability"] == 0.8
            assert voice_settings["similarity_boost"] == 0.9
            assert voice_settings["style"] == 0.5
            assert voice_settings["use_speaker_boost"] is True

    @pytest.mark.asyncio
    async def test_synthesize_speech_with_different_formats(self, adapter):
        """Test: sintetizar audio con diferentes formatos."""
        # Arrange
        text = "Test"
        audio_data = b"audio"
        mock_response = MagicMock()
        mock_response.content = audio_data
        mock_response.raise_for_status = MagicMock()

        formats = ["mp3", "wav", "ogg"]
        expected_output_formats = ["mp3_44100_128", "pcm_44100", "ogg_44100_128"]

        for fmt, expected_output in zip(formats, expected_output_formats, strict=True):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                # Act
                result = await adapter.synthesize_speech(text=text, audio_format=fmt)

                # Assert
                assert result.format == fmt
                call_kwargs = mock_client.post.call_args
                assert call_kwargs.kwargs["params"]["output_format"] == expected_output

    @pytest.mark.asyncio
    async def test_synthesize_speech_handles_http_error(self, adapter):
        """Test: manejar error HTTP de Eleven Labs."""
        # Arrange
        text = "Test"
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
                await adapter.synthesize_speech(text=text)

            assert "Error HTTP de Eleven Labs TTS" in str(exc_info.value)
            assert exc_info.value.provider == "elevenlabs"
            assert exc_info.value.original_error == http_error

    @pytest.mark.asyncio
    async def test_synthesize_speech_handles_general_error(self, adapter):
        """Test: manejar error general."""
        # Arrange
        text = "Test"
        general_error = Exception("Network error")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(side_effect=general_error)
            mock_client_class.return_value = mock_client

            # Act & Assert
            with pytest.raises(AIProviderError) as exc_info:
                await adapter.synthesize_speech(text=text)

            assert "Error en Eleven Labs TTS" in str(exc_info.value)
            assert exc_info.value.provider == "elevenlabs"
            assert exc_info.value.original_error == general_error

    @pytest.mark.asyncio
    async def test_get_available_voices(self, adapter):
        """Test: obtener voces disponibles."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "voices": [
                {"voice_id": "voice1", "name": "Voice 1"},
                {"voice_id": "voice2", "name": "Voice 2"},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            voices = await adapter.get_available_voices()

            # Assert
            assert len(voices) == 2
            assert voices[0].id == "voice1"
            assert voices[0].name == "Voice 1"
            assert voices[0].language == "multilingual"
            assert voices[0].gender == "neutral"
            assert voices[0].provider == "elevenlabs"
            assert voices[1].id == "voice2"

            mock_client.get.assert_called_once()
            call_kwargs = mock_client.get.call_args
            assert "xi-api-key" in call_kwargs.kwargs["headers"]

    @pytest.mark.asyncio
    async def test_get_available_voices_handles_error(self, adapter):
        """Test: manejar error al obtener voces."""
        # Arrange
        general_error = Exception("API error")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(side_effect=general_error)
            mock_client_class.return_value = mock_client

            # Act & Assert
            with pytest.raises(AIProviderError) as exc_info:
                await adapter.get_available_voices()

            assert "Error obteniendo voces de Eleven Labs" in str(exc_info.value)
            assert exc_info.value.provider == "elevenlabs"
            assert exc_info.value.original_error == general_error

    @pytest.mark.asyncio
    async def test_get_available_voices_with_empty_response(self, adapter):
        """Test: manejar respuesta vacía de voces."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"voices": []}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Act
            voices = await adapter.get_available_voices()

            # Assert
            assert len(voices) == 0

    def test_get_provider_name(self, adapter):
        """Test: obtener nombre del proveedor."""
        assert adapter.get_provider_name() == "elevenlabs"

    def test_get_model_info(self, adapter):
        """Test: obtener información del modelo."""
        info = adapter.get_model_info()
        assert info["provider"] == "elevenlabs"
        assert info["model"] == "eleven_multilingual_v2"
        assert "capabilities" in info
        assert "high_quality_tts" in info["capabilities"]
        assert "multilingual" in info["capabilities"]
        assert "supported_formats" in info

    def test_map_audio_format(self, adapter):
        """Test: mapeo de formatos de audio."""
        assert adapter._map_audio_format("mp3") == "mp3_44100_128"
        assert adapter._map_audio_format("wav") == "pcm_44100"
        assert adapter._map_audio_format("ogg") == "ogg_44100_128"
        # Formato desconocido usa mp3 por defecto
        assert adapter._map_audio_format("unknown") == "mp3_44100_128"
