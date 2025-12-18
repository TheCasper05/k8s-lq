"""Tests unitarios para el método start_conversation de ConversationService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.models.audio import AudioOutput
from src.domain.services.conversation_service import ConversationService
from src.interfaces.api.v1.dtos.conversation_dtos import TextAnswerResponse


@pytest.fixture
def mock_llm():
    """Crea un mock del LLMPort."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm


@pytest.fixture
def mock_tts():
    """Crea un mock del TTSPort."""
    tts = MagicMock()
    tts.synthesize_speech = AsyncMock()
    return tts


@pytest.fixture
def mock_stt():
    """Crea un mock del STTPort."""
    stt = MagicMock()
    stt.transcribe_audio = AsyncMock()
    return stt


@pytest.fixture
def conversation_service(mock_llm, mock_tts, mock_stt):
    """Crea una instancia de ConversationService con dependencias mockeadas."""
    return ConversationService(llm=mock_llm, tts=mock_tts, stt=mock_stt)


@pytest.mark.asyncio
async def test_start_conversation_success(conversation_service, mock_llm, mock_tts):
    """Test: iniciar conversación exitosamente."""
    # Arrange
    welcome_message = "Welcome! Let's practice ordering food in a restaurant."

    # Mock de process_text_answer que retorna TextAnswerResponse
    mock_text_answer_response = TextAnswerResponse(
        answer=welcome_message,
        response_id="resp_123",
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=20,
        total_tokens=30,
    )

    # Mock del TTS response
    mock_audio_output = AudioOutput(
        audio_data=b"fake_audio_data",
        format="mp3",
        duration_seconds=2.5,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )

    # Mockear process_text_answer
    with patch.object(
        conversation_service, "process_text_answer", new_callable=AsyncMock
    ) as mock_process_text_answer:
        mock_process_text_answer.return_value = mock_text_answer_response

        mock_tts.synthesize_speech.return_value = mock_audio_output

        # Act
        result = await conversation_service.start_conversation(
            scenario_type="roleplay",
            language="English",
            theme="Restaurant",
            assistant_role="waiter",
            user_role="customer",
            potential_directions="ordering food",
            setting="Italian restaurant",
            example="Customer: I'd like pizza",
            additional_data="Be polite",
            practice_topic="restaurant vocabulary",
        )

        # Assert - el método retorna una tupla
        conversation_id, response_id, audio_output = result

        assert conversation_id is not None
        assert len(conversation_id) == 36  # UUID tiene 36 caracteres
        assert response_id == "resp_123"
        assert audio_output == mock_audio_output

        # Verificar que se llamó a process_text_answer con el mensaje de inicio
        mock_process_text_answer.assert_called_once()
        call_args = mock_process_text_answer.call_args
        # Verificar que se pasó un mensaje (no verificar el contenido específico ya que puede cambiar)
        assert "message" in call_args.kwargs
        assert call_args.kwargs["response_id"] is None
        assert call_args.kwargs["scenario_type"] == "roleplay"
        assert call_args.kwargs["language"] == "English"

        # Verificar que se llamó al TTS con el mensaje correcto
        mock_tts.synthesize_speech.assert_called_once()
        tts_call_args = mock_tts.synthesize_speech.call_args
        assert tts_call_args.kwargs["text"] == welcome_message
        assert tts_call_args.kwargs["audio_format"] == "mp3"
        assert tts_call_args.kwargs["speed"] == 1.0


@pytest.mark.asyncio
async def test_start_conversation_generates_unique_ids(conversation_service, mock_llm, mock_tts):
    """Test: verificar que se generan conversation_ids únicos."""
    # Arrange
    mock_text_answer_response = TextAnswerResponse(
        answer="Welcome!",
        response_id="resp_1",
        model="gpt-4o-mini",
        input_tokens=5,
        output_tokens=5,
        total_tokens=10,
    )

    mock_audio_output = AudioOutput(
        audio_data=b"fake_audio",
        format="mp3",
        duration_seconds=1.0,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )

    with patch.object(
        conversation_service, "process_text_answer", new_callable=AsyncMock
    ) as mock_process_text_answer:
        mock_process_text_answer.return_value = mock_text_answer_response
        mock_tts.synthesize_speech.return_value = mock_audio_output

        # Act - llamar dos veces
        result1 = await conversation_service.start_conversation(
            scenario_type="roleplay",
            language="English",
            theme="Restaurant",
            assistant_role="waiter",
            user_role="customer",
            potential_directions="ordering",
            setting="Restaurant",
            example="Example",
            additional_data="Data",
            practice_topic="Topic",
        )

        result2 = await conversation_service.start_conversation(
            scenario_type="roleplay",
            language="English",
            theme="Restaurant",
            assistant_role="waiter",
            user_role="customer",
            potential_directions="ordering",
            setting="Restaurant",
            example="Example",
            additional_data="Data",
            practice_topic="Topic",
        )

        # Assert - los IDs deben ser diferentes
        conv_id1, _, _ = result1
        conv_id2, _, _ = result2
        assert conv_id1 != conv_id2


@pytest.mark.asyncio
async def test_start_conversation_audio_base64_encoding(conversation_service, mock_llm, mock_tts):
    """Test: verificar que el audio se codifica correctamente en base64."""
    # Arrange
    audio_bytes = b"test_audio_data_123"
    mock_text_answer_response = TextAnswerResponse(
        answer="Welcome!",
        response_id="resp_1",
        model="gpt-4o-mini",
        input_tokens=5,
        output_tokens=5,
        total_tokens=10,
    )

    mock_audio_output = AudioOutput(
        audio_data=audio_bytes,
        format="mp3",
        duration_seconds=1.0,
        voice_used="alloy",
        provider="openai",
        metadata={},
    )

    with patch.object(
        conversation_service, "process_text_answer", new_callable=AsyncMock
    ) as mock_process_text_answer:
        mock_process_text_answer.return_value = mock_text_answer_response
        mock_tts.synthesize_speech.return_value = mock_audio_output

        # Act
        result = await conversation_service.start_conversation(
            scenario_type="roleplay",
            language="English",
            theme="Test",
            assistant_role="assistant",
            user_role="user",
            potential_directions="directions",
            setting="setting",
            example="example",
            additional_data="data",
            practice_topic="topic",
        )

        # Assert - el método retorna una tupla con audio_output
        _, _, audio_output = result
        assert audio_output.audio_data == audio_bytes
