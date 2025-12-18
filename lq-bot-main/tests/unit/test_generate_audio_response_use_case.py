"""Tests para el caso de uso que genera respuestas de audio."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.generate_audio_response_use_case import (
    GenerateAudioResponseUseCase,
)
from src.domain.models.audio import AudioOutput


@pytest.fixture
def mock_tts():
    """Adaptador TTS con el método clave mockeado."""
    tts = MagicMock()
    tts.synthesize_speech = AsyncMock()
    return tts


@pytest.fixture
def use_case(mock_tts):
    """Caso de uso con dependencias mockeadas."""
    return GenerateAudioResponseUseCase(tts=mock_tts)


@pytest.mark.asyncio
async def test_execute_delegates_to_tts(use_case, mock_tts):
    """Se asegura que se llama al adaptador con los parámetros esperados."""
    expected_output = AudioOutput(
        audio_data=b"voice",
        format="mp3",
        duration_seconds=1.5,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )
    mock_tts.synthesize_speech.return_value = expected_output

    result = await use_case.execute(
        "Hola mundo",
        voice="alloy",
        language="es",
        audio_format="mp3",
        speed=1.3,
    )

    assert result == expected_output
    mock_tts.synthesize_speech.assert_awaited_once_with(
        text="Hola mundo",
        voice="alloy",
        language="es",
        audio_format="mp3",
        speed=1.3,
    )
