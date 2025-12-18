"""Tests unitarios para el endpoint de rúbricas."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.create_rubric_use_case import CreateRubricUseCase
from src.application.use_cases.grade_rubric_use_case import GradeRubricUseCase
from src.container import Container
from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.message import LLMResponse


@pytest.fixture
def mock_llm_adapter():
    """Crea un mock del LLM adapter."""
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
def client(mock_llm_adapter, mock_prompt_manager, mock_storage):
    """Crea un cliente de prueba con LLM, PromptManager y Storage mockeados."""
    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.interfaces.api.auth import verify_token

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Patch los factories ANTES de importar create_app
    with (
        patch(
            "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
        ) as mock_llm_factory,
        patch(
            "src.infrastructure.adapters.storage.factory.StorageProviderFactory.create_storage_adapter"
        ) as mock_storage_factory,
    ):
        mock_llm_factory.return_value = mock_llm_adapter
        mock_storage_factory.return_value = mock_storage

        from src.interfaces.api.main import create_app

        app = create_app()

        # Override de dependencias de FastAPI
        async def mock_verify_token_func(api_key: str | None = None):
            return "valid_key"

        app.dependency_overrides[verify_token] = mock_verify_token_func

        client_instance = TestClient(app)
        # Asignar los mocks como atributos para acceso en los tests
        client_instance._mock_llm = mock_llm_adapter
        client_instance._mock_prompt_manager = mock_prompt_manager
        client_instance._mock_storage = mock_storage

        # Hacer override directo de las dependencias Provide del endpoint
        # IMPORTANTE: Recrear el use case cada vez para usar los mocks actualizados
        rubric_dep = Provide[Container.create_rubric_use_case]

        def override_rubric():
            # Recrear el use case con los mocks actualizados del client
            # Esto asegura que cualquier cambio en los mocks se refleje en el use case
            return CreateRubricUseCase(
                llm=client_instance._mock_llm,
                prompt_manager=client_instance._mock_prompt_manager,
                storage=client_instance._mock_storage,
            )

        app.dependency_overrides[rubric_dep] = override_rubric

        # Override para el caso de uso de calificación
        grade_dep = Provide[Container.grade_rubric_use_case]

        def override_grade():
            # Recrear el use case con los mocks actualizados del client
            return GradeRubricUseCase(
                llm=client_instance._mock_llm,
                prompt_manager=client_instance._mock_prompt_manager,
            )

        app.dependency_overrides[grade_dep] = override_grade

        yield client_instance

        # Limpiar overrides
        app.dependency_overrides.clear()

    # Restaurar el API key original
    settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_create_rubric_with_text_success(client):
    """Test: crear rúbrica exitosamente con solo texto."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Verb tense", "metric_description": "Accuracy of verb tense usage", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}, {"name": "Pronunciation", "metric_description": "Clarity of pronunciation", "grading_type": "stars", "grading_type_description": "Stars 1-5"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=200,
        finish_reason="stop",
        metadata={"completion_tokens": 150, "prompt_tokens": 50},
        created_at=datetime.now(),
    )

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system
        "Rubric request: 'Grade verb tense and pronunciation'",  # creation_user
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

    mock_llm_adapter.generate_response.return_value = expected_llm_response

    request_data = {
        "text": "Grade verb tense and pronunciation",
    }

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "rubric" in data
    assert "metadata" in data
    assert len(data["rubric"]["metrics"]) == 2
    assert data["rubric"]["metrics"][0]["name"] == "Verb tense"
    assert data["metadata"]["provider"] == "openai"
    assert data["metadata"]["tokens_used"] == 200

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_create_rubric_with_url_success(client):
    """Test: crear rúbrica exitosamente con solo URL."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager
    mock_storage = client._mock_storage

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Grammar", "metric_description": "Correct grammar usage", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=150,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    # Mock de los prompts - debe coincidir con el orden de llamadas en el use case
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system_file (1ra llamada)
        "Rubric request (teacher text): '' Rubric request (file_id): ''",  # creation_user_file (2da llamada)
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
        },  # creation_response_schema (3ra llamada)
    ]

    mock_llm_adapter.generate_response.return_value = expected_llm_response
    # Configurar el mock del storage - el archivo existe y tiene contenido
    # IMPORTANTE: El mock ya es AsyncMock del fixture, solo configuramos return_value
    # Esto funciona igual que en test_create_rubric_use_case.py
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"PDF content"

    request_data = {
        "url": "https://example.com/rubric-guidelines.pdf",
    }

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.json()}"
    )
    data = response.json()
    assert "rubric" in data
    assert len(data["rubric"]["metrics"]) == 1
    assert data["rubric"]["metrics"][0]["name"] == "Grammar"

    # Verificar que se llamó al storage
    mock_storage.file_exists.assert_called_once()
    mock_storage.get_file.assert_called_once()


@pytest.mark.asyncio
async def test_create_rubric_with_text_and_url_success(client):
    """Test: crear rúbrica exitosamente con texto y URL."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager
    mock_storage = client._mock_storage

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Fluency", "metric_description": "Smoothness of speech", "grading_type": "percentage", "grading_type_description": "Score from 0 to 100"}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=180,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    # Mock de los prompts - debe coincidir con el orden de llamadas en el use case
    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system_file (1ra llamada)
        "Rubric request (teacher text): 'Create rubric' Rubric request (file_id): ''",  # creation_user_file (2da llamada)
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
        },  # creation_response_schema (3ra llamada)
    ]

    mock_llm_adapter.generate_response.return_value = expected_llm_response
    # Configurar el mock del storage - el archivo existe y tiene contenido
    # IMPORTANTE: El mock ya es AsyncMock del fixture, solo configuramos return_value
    # Esto funciona igual que en test_create_rubric_use_case.py
    mock_storage.file_exists.return_value = True
    mock_storage.get_file.return_value = b"PDF content"

    request_data = {
        "text": "Create rubric",
        "url": "https://example.com/guidelines.pdf",
    }

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.json()}"
    )
    data = response.json()
    assert "rubric" in data
    assert len(data["rubric"]["metrics"]) == 1
    assert data["rubric"]["metrics"][0]["name"] == "Fluency"

    # Verificar que se llamó al storage
    mock_storage.file_exists.assert_called_once()
    mock_storage.get_file.assert_called_once()


@pytest.mark.asyncio
async def test_create_rubric_validation_error_no_fields(client):
    """Test: validación cuando no se proporciona ni text ni url."""
    # Arrange - no se proporciona ni text ni url
    request_data = {}

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 422  # Unprocessable Entity
    # Verificar que el error menciona que debe haber al menos uno
    error_detail = response.json()["detail"]
    assert any(
        "text" in str(err).lower() and "url" in str(err).lower() for err in error_detail
    ) or any("debe proporcionarse al menos uno" in str(err).lower() for err in error_detail)


@pytest.mark.asyncio
async def test_create_rubric_file_not_found(client):
    """Test: manejar error cuando el archivo no existe."""
    # Arrange
    mock_storage = client._mock_storage
    mock_storage.file_exists.return_value = False  # Simular que el archivo no existe

    request_data = {
        "url": "https://example.com/non-existent-file.pdf",
    }

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 400
    assert (
        "Archivo con URL 'https://example.com/non-existent-file.pdf' no encontrado"
        in response.json()["detail"]
    )
    mock_storage.file_exists.assert_called_once()


@pytest.mark.asyncio
async def test_create_rubric_ai_error(client):
    """Test: manejar error del proveedor de IA."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",  # creation_system
        "Rubric request: 'Error test'",  # creation_user
        {"type": "object", "properties": {}},  # creation_response_schema
    ]

    mock_llm_adapter.generate_response.side_effect = AIProviderError("Error del proveedor de IA")

    request_data = {
        "text": "Error test",
    }

    # Act
    response = client.post(
        "/api/v1/rubric/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 500
    assert "Error al generar rúbrica: Error del proveedor de IA" in response.json()["detail"]
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_create_rubric_missing_api_key():
    """Test: crear rúbrica sin API key."""
    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.interfaces.api.main import create_app

    # Configurar el API key
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    app = create_app()

    # Mockear el use case para evitar llamadas reales
    mock_use_case = MagicMock(spec=CreateRubricUseCase)
    mock_use_case.execute = AsyncMock()
    app.dependency_overrides[Provide[Container.create_rubric_use_case]] = lambda: mock_use_case

    test_client = TestClient(app)

    try:
        # Arrange
        request_data = {
            "text": "Test rubric",
        }

        # Act
        response = test_client.post(
            "/api/v1/rubric/create",
            json=request_data,
            # No incluir header X-API-Key
        )

        # Assert
        assert response.status_code == 422  # FastAPI valida headers requeridos
    finally:
        app.dependency_overrides.clear()
        settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_create_rubric_invalid_api_key():
    """Test: crear rúbrica con API key inválida."""
    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.interfaces.api.main import create_app

    original_api_key = settings.api_key
    settings.api_key = "correct_key"

    app = create_app()

    # Mockear el use case para evitar llamadas reales
    mock_use_case = MagicMock(spec=CreateRubricUseCase)
    mock_use_case.execute = AsyncMock()
    app.dependency_overrides[Provide[Container.create_rubric_use_case]] = lambda: mock_use_case

    test_client = TestClient(app)

    try:
        request_data = {
            "text": "Test rubric",
        }

        # Act
        response = test_client.post(
            "/api/v1/rubric/create",
            json=request_data,
            headers={"X-API-Key": "wrong_key"},
        )

        # Assert
        assert response.status_code == 401
        assert "inválida" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
        settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_grade_rubric_success(client):
    """Test: calificar conversación exitosamente."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    conversation = """Student: Yesterday I go to the park.
Assistant: Did you enjoy it?
Student: Yes, I walk with my dog and we have fun."""

    expected_llm_response = LLMResponse(
        content='{"metrics": [{"name": "Verb tense", "grade": "65", "explanation": "Frequent incorrect past-tense forms"}, {"name": "Pronunciation", "grade": "★★★☆☆", "explanation": "Pronunciation was mostly clear"}]}',
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

    mock_llm_adapter.generate_response.return_value = expected_llm_response

    request_data = {
        "conversation": conversation,
        "rubric": {
            "metrics": [
                {
                    "name": "Verb tense",
                    "metric_description": "Accuracy of verb tense usage",
                    "grading_type": "percentage",
                    "grading_type_description": "Score from 0 to 100",
                },
                {
                    "name": "Pronunciation",
                    "metric_description": "Clarity of pronunciation",
                    "grading_type": "stars",
                    "grading_type_description": "Stars 1-5",
                },
            ],
        },
    }

    # Act
    response = client.post(
        "/api/v1/rubric/grade",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "grade" in data
    assert "metadata" in data
    assert len(data["grade"]["metrics"]) == 2
    assert data["grade"]["metrics"][0]["name"] == "Verb tense"
    assert data["grade"]["metrics"][0]["grade"] == "65"
    assert data["metadata"]["provider"] == "openai"
    assert data["metadata"]["tokens_used"] == 200

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_grade_rubric_empty_conversation(client):
    """Test: error cuando la conversación está vacía."""
    # Arrange
    request_data = {
        "conversation": "",
        "rubric": {
            "metrics": [
                {
                    "name": "Verb tense",
                    "metric_description": "Accuracy",
                    "grading_type": "percentage",
                    "grading_type_description": "Score from 0 to 100",
                },
            ],
        },
    }

    # Act
    response = client.post(
        "/api/v1/rubric/grade",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 400
    assert "La conversación no puede estar vacía" in response.json()["detail"]


@pytest.mark.asyncio
async def test_grade_rubric_empty_rubric(client):
    """Test: error cuando la rúbrica no tiene métricas."""
    # Arrange
    request_data = {
        "conversation": "Student: Hello",
        "rubric": {"metrics": []},
    }

    # Act
    response = client.post(
        "/api/v1/rubric/grade",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 400
    assert "La rúbrica debe contener al menos una métrica" in response.json()["detail"]


@pytest.mark.asyncio
async def test_grade_rubric_ai_error(client):
    """Test: manejar error del proveedor de IA."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    mock_prompt_manager.render.side_effect = [
        "You are asked with aiding teachers...",
        "Conversation: '...' Metrics: '...'",
        {"type": "object", "properties": {}},
    ]

    mock_llm_adapter.generate_response.side_effect = AIProviderError("Error del proveedor de IA")

    request_data = {
        "conversation": "Student: Hello",
        "rubric": {
            "metrics": [
                {
                    "name": "Verb tense",
                    "metric_description": "Accuracy",
                    "grading_type": "percentage",
                    "grading_type_description": "Score from 0 to 100",
                },
            ],
        },
    }

    # Act
    response = client.post(
        "/api/v1/rubric/grade",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 500
    assert "Error al calificar conversación: Error del proveedor de IA" in response.json()["detail"]
    mock_llm_adapter.generate_response.assert_called_once()
