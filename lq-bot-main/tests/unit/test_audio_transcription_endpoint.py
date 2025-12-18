"""Tests unitarios para el endpoint de transcripción de audio."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.models.audio import TranscriptionResult


class TestTranscriptionEndpoint:
    """Tests para el endpoint de transcripción."""

    @pytest.fixture
    def mock_use_case(self):
        """Crea un mock del caso de uso."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        use_case.stt = MagicMock()
        use_case.stt.model = "whisper-1"
        return use_case

    @pytest.fixture
    def mock_storage_adapter(self):
        """Crea un mock del storage adapter."""
        adapter = MagicMock()
        adapter.get_file = AsyncMock(return_value=b"audio data")
        return adapter

    @pytest.mark.asyncio
    async def test_transcribe_with_file(self, mock_use_case, mock_storage_adapter):
        """Test: transcribe audio desde form data con file."""
        from fastapi import Request

        from src.interfaces.api.v1.audio_routes import transcribe_audio

        test_data = b"audio binary"

        # Crear un mock de Request con form data
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "multipart/form-data"

        # Mock del form
        mock_form = MagicMock()
        mock_file_obj = MagicMock()
        mock_file_obj.read = AsyncMock(return_value=test_data)
        mock_form.__getitem__ = MagicMock(
            side_effect=lambda key: {"file": mock_file_obj, "language": "en"}.get(key)
        )
        mock_form.__contains__ = MagicMock(side_effect=lambda key: key in ["file", "language"])
        mock_request.form = AsyncMock(return_value=mock_form)

        mock_result = TranscriptionResult(
            text="Hello world",
            language="en",
            confidence=0.95,
            provider="openai",
            duration_seconds=1.5,
            metadata={},
        )
        mock_use_case.execute.return_value = mock_result
        mock_use_case.stt.model = "whisper-1"

        with patch("src.interfaces.api.v1.audio_routes.verify_token", return_value="valid_key"):
            response = await transcribe_audio(
                http_request=mock_request,
                api_key="valid_key",
                use_case=mock_use_case,
                storage_adapter=mock_storage_adapter,
            )

            assert response.transcription == "Hello world"
            assert response.provider == "openai"
            assert response.model == "whisper-1"
            mock_use_case.execute.assert_called_once()
            # Verificar que se pasó el audio
            call_args = mock_use_case.execute.call_args
            assert call_args.kwargs["audio"] == test_data
