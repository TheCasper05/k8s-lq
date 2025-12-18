"""Tests unitarios para el adaptador OpenAI STT."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infrastructure.adapters.ai.openai.openai_stt_adapter import OpenAISTTAdapter


@pytest.mark.asyncio
async def test_transcribe_audio_calls_openai_and_returns_result():
    adapter = OpenAISTTAdapter(api_key="key", model="whisper-1")
    response = SimpleNamespace(text="hola", language="es", confidence=0.85, duration=1.4)

    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.transcriptions = MagicMock()
    mock_client.audio.transcriptions.create = AsyncMock(return_value=response)

    adapter.client = mock_client

    result = await adapter.transcribe_audio(b"\x00\x01", language="es", temperature=0.2)

    assert result.text == "hola"
    assert result.language == "es"
    assert result.duration_seconds == 1.4
    mock_client.audio.transcriptions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_translate_audio_uses_translation_endpoint():
    adapter = OpenAISTTAdapter(api_key="key")
    translation_response = SimpleNamespace(
        text="hello", language="en", confidence=0.92, duration=2.0
    )

    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.translations = MagicMock()
    mock_client.audio.translations.create = AsyncMock(return_value=translation_response)

    adapter.client = mock_client

    result = await adapter.translate_audio(
        b"\x00", target_language="en", temperature=0.3, extra="param"
    )

    assert result.text == "hello"
    mock_client.audio.translations.create.assert_awaited_once()

    call_kwargs = mock_client.audio.translations.create.call_args.kwargs
    assert call_kwargs["language"] == "en"
    assert call_kwargs["temperature"] == 0.3
    assert call_kwargs["extra"] == "param"


@pytest.mark.asyncio
async def test_translate_falls_back_to_transcribe_if_endpoint_missing():
    adapter = OpenAISTTAdapter(api_key="key")

    # Mock the client and audio object
    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.translations = None  # Simulate missing translations endpoint

    adapter.client = mock_client

    expected = SimpleNamespace(text="fallback", language="en", confidence=0.5, duration=0.7)
    adapter.transcribe_audio = AsyncMock(return_value=expected)

    result = await adapter.translate_audio(b"", target_language="en", temperature=0.4)

    assert result.text == "fallback"
    adapter.transcribe_audio.assert_awaited_once_with(audio=b"", language="en", temperature=0.4)
