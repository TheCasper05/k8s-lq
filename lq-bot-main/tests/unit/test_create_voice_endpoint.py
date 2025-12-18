"""Tests unitarios para el endpoint de creación de voz (TTS)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from src.domain.models.audio import AudioOutput
from src.interfaces.api.v1.audio_routes import create_voice


class TestCreateVoiceEndpoint:
    """Tests para el endpoint create_voice."""

    @pytest.fixture
    def mock_use_case(self):
        """Crea un mock del caso de uso."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        return use_case

    @pytest.fixture
    def mock_storage_adapter(self):
        """Crea un mock del storage adapter."""
        from src.infrastructure.adapters.storage.boto3_storage_adapter import Boto3StorageAdapter

        # Crear un mock que pase isinstance check
        adapter = MagicMock()
        adapter.save_file = AsyncMock(return_value="audio/tts/test_audio.mp3")
        adapter.get_public_url = MagicMock(
            return_value="https://example.com/audio/tts/test_audio.mp3"
        )
        # Hacer que isinstance(adapter, Boto3StorageAdapter) retorne True
        # Usando __class__ para que isinstance funcione
        adapter.__class__ = Boto3StorageAdapter
        return adapter

    @pytest.fixture
    def mock_audio_output(self):
        """Crea un mock de AudioOutput."""
        return AudioOutput(
            audio_data=b"fake audio data",
            format="mp3",
            duration_seconds=2.5,
            voice_used="alloy",
            provider="openai",
            metadata={"model": "tts-1"},
        )

    @pytest.mark.asyncio
    async def test_create_voice_success(
        self, mock_use_case, mock_storage_adapter, mock_audio_output
    ):
        """Test: generar audio exitosamente."""
        from src.interfaces.api.v1.dtos.audio_dtos import CreateVoiceRequest

        mock_use_case.execute.return_value = mock_audio_output

        # Crear una instancia real del DTO
        request = CreateVoiceRequest(
            text="Hello, this is a test",
            voice="alloy",
            audio_format="mp3",
            speed=1.0,
        )

        with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
            response = await create_voice(
                request=request,
                api_key="valid_key",
                use_case=mock_use_case,
                storage_adapter=mock_storage_adapter,
            )

            # Verificar que se llamó al use case con los parámetros correctos
            mock_use_case.execute.assert_called_once()
            call_kwargs = mock_use_case.execute.call_args.kwargs
            assert call_kwargs["text"] == "Hello, this is a test"
            assert call_kwargs["voice"] == "alloy"
            assert call_kwargs["audio_format"] == "mp3"
            assert call_kwargs["speed"] == 1.0

            # Verificar que se guardó el archivo en storage
            mock_storage_adapter.save_file.assert_called_once()
            save_call_kwargs = mock_storage_adapter.save_file.call_args.kwargs
            assert save_call_kwargs["file_data"] == b"fake audio data"
            assert save_call_kwargs["folder"] == "audio/tts"
            assert "metadata" in save_call_kwargs

            # Verificar la respuesta
            assert response.url == "https://example.com/audio/tts/test_audio.mp3"
            assert response.key == "audio/tts/test_audio.mp3"
            assert response.duration_seconds == 2.5
            assert response.voice_used == "alloy"
            assert response.provider == "openai"
            assert response.format == "mp3"

    @pytest.mark.asyncio
    async def test_create_voice_with_defaults(
        self, mock_use_case, mock_storage_adapter, mock_audio_output
    ):
        """Test: generar audio con valores por defecto."""
        from src.interfaces.api.v1.dtos.audio_dtos import CreateVoiceRequest

        mock_use_case.execute.return_value = mock_audio_output

        # Crear una instancia real del DTO para que respete los valores por defecto
        request = CreateVoiceRequest(text="Test text")

        with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
            await create_voice(
                request=request,
                api_key="valid_key",
                use_case=mock_use_case,
                storage_adapter=mock_storage_adapter,
            )

            # Verificar que se usaron los valores por defecto
            call_kwargs = mock_use_case.execute.call_args.kwargs
            assert call_kwargs["voice"] == "default"
            assert call_kwargs["audio_format"] == "mp3"
            assert call_kwargs["speed"] == 1.0

    @pytest.mark.asyncio
    async def test_create_voice_different_formats(self, mock_use_case, mock_storage_adapter):
        """Test: generar audio en diferentes formatos."""
        from src.interfaces.api.v1.dtos.audio_dtos import CreateVoiceRequest

        formats = ["mp3", "ogg", "wav"]

        for audio_format in formats:
            mock_audio_output = AudioOutput(
                audio_data=b"fake audio data",
                format=audio_format,
                duration_seconds=1.0,
                voice_used="alloy",
                provider="openai",
                metadata={},
            )
            mock_use_case.execute.return_value = mock_audio_output

            # Crear una instancia real del DTO
            request = CreateVoiceRequest(
                text="Test",
                audio_format=audio_format,
            )

            with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
                await create_voice(
                    request=request,
                    api_key="valid_key",
                    use_case=mock_use_case,
                    storage_adapter=mock_storage_adapter,
                )

                # Verificar que se llamó con el formato correcto
                call_kwargs = mock_use_case.execute.call_args.kwargs
                assert call_kwargs["audio_format"] == audio_format

    @pytest.mark.asyncio
    async def test_create_voice_tts_error(self, mock_use_case, mock_storage_adapter):
        """Test: manejo de error del TTS."""
        from src.domain.exceptions.ai_exceptions import AIProviderError
        from src.interfaces.api.v1.dtos.audio_dtos import CreateVoiceRequest

        # Simular error del TTS
        mock_use_case.execute.side_effect = AIProviderError("Error en TTS", provider="openai")

        # Crear una instancia real del DTO
        request = CreateVoiceRequest(text="Test")

        with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
            with pytest.raises(HTTPException) as exc_info:
                await create_voice(
                    request=request,
                    api_key="valid_key",
                    use_case=mock_use_case,
                    storage_adapter=mock_storage_adapter,
                )

            assert exc_info.value.status_code == 500
            assert "Error al generar audio" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_create_voice_saves_to_storage(
        self, mock_use_case, mock_storage_adapter, mock_audio_output
    ):
        """Test: guarda archivo en storage correctamente."""
        from src.interfaces.api.v1.dtos.audio_dtos import CreateVoiceRequest

        mock_use_case.execute.return_value = mock_audio_output

        # Crear una instancia real del DTO
        request = CreateVoiceRequest(
            text="Test",
            audio_format="mp3",
        )

        with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
            await create_voice(
                request=request,
                api_key="valid_key",
                use_case=mock_use_case,
                storage_adapter=mock_storage_adapter,
            )

            # Verificar que se guardó el archivo en storage
            mock_storage_adapter.save_file.assert_called_once()
            save_call = mock_storage_adapter.save_file.call_args
            assert save_call.kwargs["file_data"] == b"fake audio data"
            assert save_call.kwargs["folder"] == "audio/tts"
            assert "metadata" in save_call.kwargs
            assert save_call.kwargs["metadata"]["provider"] == "openai"
            assert save_call.kwargs["metadata"]["format"] == "mp3"
