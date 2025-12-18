"""Tests unitarios para el caso de uso de calificación de rúbricas."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.grade_rubric_use_case import GradeRubricUseCase
from src.domain.models.message import LLMResponse
from src.domain.models.rubric import Metric, Rubric, RubricGrade, RubricGradeMetadata


@pytest.fixture
def mock_llm():
    """Crea un mock del LLM adapter."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm


@pytest.fixture
def mock_prompt_manager():
    """Crea un mock del PromptManager."""
    pm = MagicMock()
    pm.render = MagicMock()
    return pm


@pytest.fixture
def use_case(mock_llm, mock_prompt_manager):
    """Crea una instancia del caso de uso con mocks."""
    return GradeRubricUseCase(llm=mock_llm, prompt_manager=mock_prompt_manager)


@pytest.fixture
def sample_rubric():
    """Crea una rúbrica de ejemplo."""
    metrics = [
        Metric(
            name="Verb tense",
            metric_description="Accuracy of verb tense usage",
            grading_type="percentage",
            grading_type_description="Score from 0 to 100",
        ),
        Metric(
            name="Pronunciation",
            metric_description="Clarity of pronunciation",
            grading_type="stars",
            grading_type_description="Stars 1-5",
        ),
    ]
    return Rubric(metrics=metrics)


@pytest.fixture
def sample_conversation():
    """Crea una conversación de ejemplo."""
    return """Student: Yesterday I go to the park.
Assistant: Did you enjoy it?
Student: Yes, I walk with my dog and we have fun."""


@pytest.mark.asyncio
async def test_execute_grades_conversation_successfully(
    use_case, mock_llm, mock_prompt_manager, sample_rubric, sample_conversation
):
    """Test: calificar conversación exitosamente."""
    # Arrange
    expected_response = {
        "metrics": [
            {
                "name": "Verb tense",
                "grade": "65",
                "explanation": "Frequent incorrect past-tense forms (e.g., 'Yesterday I go', 'I walk') lowered accuracy.",
            },
            {
                "name": "Pronunciation",
                "grade": "★★★☆☆",
                "explanation": "Pronunciation was mostly clear but final consonants in 'walked' and 'parked' were dropped.",
            },
        ]
    }

    expected_llm_response = LLMResponse(
        content=json.dumps(expected_response),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=200,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # grading_system
        "Conversation: '...' Metrics: '...'",  # grading_user
        {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "grade": {"type": "string"},
                            "explanation": {"type": "string"},
                        },
                    },
                },
            },
        },  # grading_response_schema
    ]

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    rubric_grade, rubric_grade_metadata = await use_case.execute(
        conversation=sample_conversation,
        rubric=sample_rubric,
    )

    # Assert
    assert isinstance(rubric_grade, RubricGrade)
    assert len(rubric_grade.metrics) == 2
    assert rubric_grade.metrics[0].name == "Verb tense"
    assert rubric_grade.metrics[0].grade == "65"
    assert "incorrect past-tense" in rubric_grade.metrics[0].explanation.lower()

    assert isinstance(rubric_grade_metadata, RubricGradeMetadata)
    assert rubric_grade_metadata.provider == "openai"
    assert rubric_grade_metadata.tokens_used == 200

    # Verificar que se llamó al LLM
    mock_llm.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_execute_raises_error_when_conversation_empty(use_case, sample_rubric):
    """Test: lanza error cuando la conversación está vacía."""
    # Act & Assert
    with pytest.raises(ValueError, match="La conversación no puede estar vacía"):
        await use_case.execute(conversation="", rubric=sample_rubric)

    with pytest.raises(ValueError, match="La conversación no puede estar vacía"):
        await use_case.execute(conversation="   ", rubric=sample_rubric)


@pytest.mark.asyncio
async def test_execute_raises_error_when_rubric_empty(use_case, sample_conversation):
    """Test: lanza error cuando la rúbrica no tiene métricas."""
    # Arrange
    empty_rubric = Rubric(metrics=[])

    # Act & Assert
    with pytest.raises(ValueError, match="La rúbrica debe contener al menos una métrica"):
        await use_case.execute(conversation=sample_conversation, rubric=empty_rubric)


@pytest.mark.asyncio
async def test_execute_handles_json_decode_error(
    use_case, mock_llm, mock_prompt_manager, sample_rubric, sample_conversation
):
    """Test: maneja errores de parseo JSON."""
    # Arrange
    invalid_json_response = LLMResponse(
        content="This is not valid JSON",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",
        "Conversation: '...' Metrics: '...'",
        {"type": "object", "properties": {}},
    ]

    mock_llm.generate_response.return_value = invalid_json_response

    # Act & Assert
    with pytest.raises(ValueError, match="No se pudo parsear la respuesta como JSON"):
        await use_case.execute(conversation=sample_conversation, rubric=sample_rubric)


@pytest.mark.asyncio
async def test_execute_extracts_json_from_markdown(
    use_case, mock_llm, mock_prompt_manager, sample_rubric, sample_conversation
):
    """Test: extrae JSON de respuesta con markdown."""
    # Arrange
    markdown_response = """Here's the result:

```json
{
  "metrics": [
    {
      "name": "Verb tense",
      "grade": "70",
      "explanation": "Some errors in past tense usage."
    }
  ]
}
```"""

    expected_llm_response = LLMResponse(
        content=markdown_response,
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=150,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",
        "Conversation: '...' Metrics: '...'",
        {"type": "object", "properties": {}},
    ]

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    rubric_grade, _ = await use_case.execute(
        conversation=sample_conversation,
        rubric=sample_rubric,
    )

    # Assert
    assert len(rubric_grade.metrics) == 1
    assert rubric_grade.metrics[0].name == "Verb tense"
    assert rubric_grade.metrics[0].grade == "70"


@pytest.mark.asyncio
async def test_execute_uses_custom_temperature_and_max_tokens(
    use_case, mock_llm, mock_prompt_manager, sample_rubric, sample_conversation
):
    """Test: usa temperatura y max_tokens personalizados."""
    # Arrange
    expected_response = {"metrics": [{"name": "Verb tense", "grade": "70", "explanation": "Good"}]}
    expected_llm_response = LLMResponse(
        content=json.dumps(expected_response),
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",
        "Conversation: '...' Metrics: '...'",
        {"type": "object", "properties": {}},
    ]

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    await use_case.execute(
        conversation=sample_conversation,
        rubric=sample_rubric,
        temperature=0.5,
        max_tokens=2000,
    )

    # Assert
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs["temperature"] == 0.5
    assert call_args.kwargs["max_tokens"] == 2000
