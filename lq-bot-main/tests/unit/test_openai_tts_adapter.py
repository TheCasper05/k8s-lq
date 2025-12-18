"""Tests unitarios para el adaptador OpenAI TTS."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infrastructure.adapters.ai.openai.openai_tts_adapter import OpenAITTSAdapter


@pytest.mark.asyncio
async def test_synthesize_speech_calls_openai_and_returns_audio():
    adapter = OpenAITTSAdapter(api_key="key", model="tts-1", voice="alloy")
    response = SimpleNamespace(audio=b"binary")

    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.speech = MagicMock()
    mock_client.audio.speech.create = AsyncMock(return_value=response)

    adapter.client = mock_client

    output = await adapter.synthesize_speech(
        "Hola", voice="luna", language="es", audio_format="mp3", speed=1.2, style="soft"
    )

    assert output.audio_data == b"binary"
    assert output.format == "mp3"
    assert output.voice_used == "luna"
    assert output.metadata["model"] == "tts-1"
    assert output.metadata["extra"]["style"] == "soft"
    mock_client.audio.speech.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_available_voices_filters_by_language():
    adapter = OpenAITTSAdapter(api_key="key")
    voice_data = [
        {"id": "alloy", "name": "Alloy", "language": "en", "gender": "neutral"},
        {"id": "luna", "name": "Luna", "language": "es", "gender": "female"},
    ]
    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.speech = MagicMock()
    mock_client.audio.speech.list_voices = AsyncMock(return_value=SimpleNamespace(data=voice_data))

    adapter.client = mock_client

    result = await adapter.get_available_voices(language="es")

    assert len(result) == 1
    assert result[0].id == "luna"
    mock_client.audio.speech.list_voices.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_available_voices_uses_defaults_when_endpoint_empty():
    adapter = OpenAITTSAdapter(api_key="key")
    mock_client = MagicMock()
    mock_client.audio = MagicMock()
    mock_client.audio.speech = MagicMock()
    mock_client.audio.speech.list_voices = AsyncMock(return_value=SimpleNamespace(data=[]))

    adapter.client = mock_client

    result = await adapter.get_available_voices()

    assert len(result) == 3
    ids = {voice.id for voice in result}
    assert "alloy" in ids
    mock_client.audio.speech.list_voices.assert_awaited_once()
