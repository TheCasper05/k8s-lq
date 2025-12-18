"""Tests para el caso de uso de generación de transcripciones."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.generate_transcription_use_case import (
    GenerateTranscriptionUseCase,
)
from src.domain.models.audio import TranscriptionResult


@pytest.fixture
def mock_stt():
    """Adaptador STT con métodos asíncronos mockeados."""
    stt = MagicMock()
    stt.transcribe_audio = AsyncMock()
    stt.translate_audio = AsyncMock()
    return stt


@pytest.fixture
def use_case(mock_stt):
    """Instancia del caso de uso con dependencias mockeadas."""
    return GenerateTranscriptionUseCase(stt=mock_stt)


@pytest.mark.asyncio
async def test_execute_transcribes_audio_when_translate_false(use_case, mock_stt):
    """Verifica que el caso de uso llama al adaptador para transcribir."""
    expected = TranscriptionResult(
        text="hola",
        language="es",
        confidence=0.9,
        provider="openai",
        duration_seconds=1.2,
        metadata={},
    )
    mock_stt.transcribe_audio.return_value = expected

    audio_payload = b"dummy"
    result = await use_case.execute(audio_payload, language="es")

    assert result == expected
    mock_stt.transcribe_audio.assert_awaited_once_with(
        audio=audio_payload, language="es", temperature=0.0
    )


@pytest.mark.asyncio
async def test_execute_translates_when_flag_enabled(use_case, mock_stt):
    """Verifica que se llama a translate_audio cuando se solicita traducción."""
    expected = TranscriptionResult(
        text="hello",
        language="en",
        confidence=0.8,
        provider="openai",
        duration_seconds=1.0,
        metadata={},
    )
    mock_stt.translate_audio.return_value = expected

    result = await use_case.execute(
        b"dummy",
        translate=True,
        target_language="en",
        temperature=0.5,
    )

    assert result == expected
    mock_stt.translate_audio.assert_awaited_once_with(
        audio=b"dummy", target_language="en", temperature=0.5
    )


@pytest.mark.asyncio
async def test_execute_requires_target_language_when_translating(use_case):
    """Si se pide traducción sin idioma destino, se lanza ValueError."""
    with pytest.raises(ValueError):
        await use_case.execute(b"audio", translate=True)
