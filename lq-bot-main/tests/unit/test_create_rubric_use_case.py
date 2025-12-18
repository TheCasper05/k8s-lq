"""Tests unitarios para CreateRubricUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.use_cases.create_rubric_use_case import CreateRubricUseCase
from src.domain.models.message import LLMResponse
from src.domain.models.rubric import Rubric, RubricMetadata


@pytest.fixture
def mock_llm():
    """Crea un mock del LLMPort."""
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    llm.get_provider_name = MagicMock(return_value="openai")
    llm.get_model_info = MagicMock(return_value={"name": "gpt-4o-mini"})
    return llm


@pytest.fixture
def mock_prompt_manager():
    """Crea un mock del PromptManager."""
    pm = MagicMock()
    pm.render = MagicMock()
    return pm


@pytest.fixture
def mock_storage():
    """Crea un mock del FileStoragePort."""
    storage = MagicMock()
    storage.file_exists = AsyncMock(return_value=True)
    storage.get_file = AsyncMock(return_value=b"file content")
    return storage


@pytest.fixture
def use_case(mock_llm, mock_prompt_manager, mock_storage):
    """Crea una instancia del caso de uso con dependencias mockeadas."""
    return CreateRubricUseCase(
        llm=mock_llm, prompt_manager=mock_prompt_manager, storage=mock_storage
    )


@pytest.fixture
def use_case_no_storage(mock_llm, mock_prompt_manager):
    """Crea una instancia del caso de uso sin storage."""
    return CreateRubricUseCase(llm=mock_llm, prompt_manager=mock_prompt_manager, storage=None)


@pytest.mark.asyncio
async def test_execute_creates_rubric_with_text_only(use_case, mock_llm, mock_prompt_manager):
    """Test: crear rúbrica solo con texto."""
    # Arrange
    text = "Grade verb tense accuracy (percentage) and pronunciation (stars)."

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system
        f"Rubric request: '{text}'",  # creation_user
        {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "metric_description": {"type": "string"},
                            "grading_type": {"type": "string"},
                            "grading_type_description": {"type": "string"},
                        },
                    },
                },
            },
        },  # creation_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Verb tense", "metric_description": "Accuracy of verb tense usage", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}, {"name": "Pronunciation", "metric_description": "Clarity of pronunciation", "grading_type": "stars", "grading_type_description": "Stars 1-5"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=150,
        finish_reason="stop",
        metadata={"completion_tokens": 100, "prompt_tokens": 50},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    rubric, rubric_metadata = await use_case.execute(text=text)

    # Assert
    assert isinstance(rubric, Rubric)
    assert len(rubric.metrics) == 2
    assert rubric.metrics[0].name == "Verb tense"
    assert rubric.metrics[0].grading_type == "percentage"
    assert rubric.metrics[1].name == "Pronunciation"
    assert rubric.metrics[1].grading_type == "stars"
    assert isinstance(rubric_metadata, RubricMetadata)
    assert rubric_metadata.provider == "openai"
    assert rubric_metadata.tokens_used == 150
    mock_llm.generate_response.assert_called_once()
    assert mock_prompt_manager.render.call_count == 3


@pytest.mark.asyncio
async def test_execute_creates_rubric_with_file_only(
    use_case, mock_llm, mock_prompt_manager, mock_storage
):
    """Test: crear rúbrica solo con archivo."""
    # Arrange
    file_url = "https://example.com/rubric-guidelines.pdf"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system_file
        "Rubric request (teacher text): '' Rubric request (file_id): ''",  # creation_user_file
        {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "metric_description": {"type": "string"},
                            "grading_type": {"type": "string"},
                            "grading_type_description": {"type": "string"},
                        },
                    },
                },
            },
        },  # creation_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Grammar", "metric_description": "Correct grammar usage", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"PDF content here"

    # Act
    rubric, _ = await use_case.execute(text=None, file_url=file_url)

    # Assert
    assert isinstance(rubric, Rubric)
    assert len(rubric.metrics) == 1
    assert rubric.metrics[0].name == "Grammar"
    mock_llm.generate_response.assert_called_once()
    # Verificar que se pasaron archivos al LLM
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs.get("files") is not None
    assert len(call_args.kwargs["files"]) == 1


@pytest.mark.asyncio
async def test_execute_creates_rubric_with_text_and_file(
    use_case, mock_llm, mock_prompt_manager, mock_storage
):
    """Test: crear rúbrica con texto y archivo."""
    # Arrange
    text = "Create a rubric for evaluating conversation skills"
    file_url = "https://example.com/guidelines.pdf"

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system_file
        f"Rubric request (teacher text): '{text}' Rubric request (file_id): ''",  # creation_user_file
        {
            "type": "object",
            "properties": {
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "metric_description": {"type": "string"},
                            "grading_type": {"type": "string"},
                            "grading_type_description": {"type": "string"},
                        },
                    },
                },
            },
        },  # creation_response_schema
    ]

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Fluency", "metric_description": "Smoothness of speech", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=120,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"PDF content"

    # Act
    rubric, _ = await use_case.execute(text=text, file_url=file_url)

    # Assert
    assert isinstance(rubric, Rubric)
    assert len(rubric.metrics) == 1
    assert rubric.metrics[0].name == "Fluency"
    # Verificar que se pasaron archivos
    call_args = mock_llm.generate_response.call_args
    assert call_args.kwargs.get("files") is not None


@pytest.mark.asyncio
async def test_execute_raises_error_when_no_text_or_file(use_case):
    """Test: lanzar error cuando no hay texto ni archivo."""
    # Act & Assert
    with pytest.raises(ValueError, match="Debe proporcionarse al menos uno de los campos"):
        await use_case.execute(text=None, file_url=None)


@pytest.mark.asyncio
async def test_execute_raises_error_when_file_not_found(use_case, mock_storage):
    """Test: lanzar error cuando el archivo no existe."""
    # Arrange
    file_url = "https://example.com/nonexistent.pdf"
    mock_storage.file_exists.return_value = False

    # Act & Assert
    with pytest.raises(ValueError, match=r"Archivo con URL.*no encontrado"):
        await use_case.execute(text=None, file_url=file_url)


@pytest.mark.asyncio
async def test_execute_raises_error_when_storage_not_available(use_case_no_storage):
    """Test: lanzar error cuando storage no está disponible pero se requiere archivo."""
    # Arrange
    file_url = "https://example.com/file.pdf"

    # Act & Assert
    with pytest.raises(ValueError, match="Storage adapter no disponible"):
        await use_case_no_storage.execute(text=None, file_url=file_url)


@pytest.mark.asyncio
async def test_execute_handles_json_decode_error(use_case, mock_llm, mock_prompt_manager):
    """Test: manejar error de parsing JSON cuando el LLM devuelve texto adicional."""
    # Arrange
    text = "Grade verb tense"

    mock_prompt_manager.render.side_effect = [
        "You are asked...",
        f"Rubric request: '{text}'",
        {"type": "object", "properties": {}},
    ]

    # LLM devuelve JSON con texto adicional
    expected_llm_response = LLMResponse(
        content='Here is the rubric:\n{"metrics": [{"name": "Verb tense", "metric_description": "Test", "grading_type": "percentage", "grading_type_description": "0-100"}]}\nEnd.',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    rubric, _ = await use_case.execute(text=text)

    # Assert
    assert isinstance(rubric, Rubric)
    assert len(rubric.metrics) == 1
    assert rubric.metrics[0].name == "Verb tense"


@pytest.mark.asyncio
async def test_execute_raises_error_on_invalid_json(use_case, mock_llm, mock_prompt_manager):
    """Test: lanzar error cuando no se puede parsear JSON."""
    # Arrange
    text = "Grade verb tense"

    mock_prompt_manager.render.side_effect = [
        "You are asked...",
        f"Rubric request: '{text}'",
        {"type": "object", "properties": {}},
    ]

    # LLM devuelve contenido que no es JSON válido
    expected_llm_response = LLMResponse(
        content="This is not valid JSON at all",
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act & Assert
    with pytest.raises(ValueError, match="No se pudo parsear la respuesta como JSON"):
        await use_case.execute(text=text)


@pytest.mark.asyncio
async def test_execute_detects_mime_type_from_file(
    use_case, mock_llm, mock_prompt_manager, mock_storage
):
    """Test: detectar MIME type correctamente desde el archivo."""
    # Arrange
    file_url = "https://example.com/document.pdf"
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"PDF content"

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object", "properties": {}},
    ]

    expected_llm_response = LLMResponse(
        content='{"metrics": []}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    await use_case.execute(text=None, file_url=file_url)

    # Assert
    call_args = mock_llm.generate_response.call_args
    files = call_args.kwargs.get("files")
    assert files is not None
    assert len(files) == 1
    filename, file_data, mime_type = files[0]
    assert filename == "document.pdf"
    assert mime_type == "application/pdf"
    assert file_data == b"PDF content"


@pytest.mark.asyncio
async def test_execute_uses_default_mime_type_when_unknown(
    use_case, mock_llm, mock_prompt_manager, mock_storage
):
    """Test: usar MIME type por defecto cuando no se puede detectar."""
    # Arrange
    file_url = "https://example.com/file.unknown"
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"Content"

    mock_prompt_manager.render.side_effect = [
        "System prompt",
        "User prompt",
        {"type": "object", "properties": {}},
    ]

    expected_llm_response = LLMResponse(
        content='{"metrics": []}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=50,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    mock_llm.generate_response.return_value = expected_llm_response

    # Act
    await use_case.execute(text=None, file_url=file_url)

    # Assert
    call_args = mock_llm.generate_response.call_args
    files = call_args.kwargs.get("files")
    assert files is not None
    _, _, mime_type = files[0]
    assert mime_type == "application/octet-stream"  # Default MIME type
