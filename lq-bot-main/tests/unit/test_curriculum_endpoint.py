"""Tests unitarios para el endpoint de currículos."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.generate_curriculum_use_case import CurriculumGeneratorUseCase

# Importar Container para poder hacer patch
# NO importar curriculum_routes aquí para evitar que Provide se resuelva antes del patch
from src.container import Container
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
def client(mock_llm_adapter, mock_prompt_manager):
    """Crea un cliente de prueba con LLM y PromptManager mockeados."""
    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.container import Container
    from src.interfaces.api.auth import verify_token

    # Configurar el API key en settings para que coincida con los tests
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Crear caso de uso real pero con LLM y PromptManager mockeados
    real_curriculum_use_case = CurriculumGeneratorUseCase(
        llm=mock_llm_adapter, prompt_manager=mock_prompt_manager
    )

    # Patch el factory de LLM ANTES de importar create_app (esto evita crear un LLM real)
    with patch(
        "src.infrastructure.adapters.ai.factory.AIProviderFactory.create_llm_adapter"
    ) as mock_llm_factory:
        mock_llm_factory.return_value = mock_llm_adapter

        from src.interfaces.api.main import create_app

        app = create_app()

        # Override de dependencias de FastAPI - siempre retorna valid_key para tests exitosos
        async def mock_verify_token_func(api_key: str | None = None):
            # Para tests que esperan éxito, siempre retornar valid_key
            return "valid_key"

        app.dependency_overrides[verify_token] = mock_verify_token_func

        # Hacer override directo de las dependencias Provide del endpoint
        curriculum_dep = Provide[Container.generate_curriculum_use_case]

        def override_curriculum():
            return real_curriculum_use_case

        app.dependency_overrides[curriculum_dep] = override_curriculum

        client_instance = TestClient(app)
        # Asignar los mocks como atributos para acceso en los tests
        client_instance._mock_llm = mock_llm_adapter
        client_instance._mock_prompt_manager = mock_prompt_manager

        yield client_instance

        # Limpiar overrides
        app.dependency_overrides.clear()

    # Restaurar el API key original
    settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_create_curriculum_success(client):
    """Test: crear currículo exitosamente."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    expected_llm_response = LLMResponse(
        content='{"name": "Curso de Español Básico", "description": "Curso introductorio de español nivel A1", "submodules": [{"name": "Saludos y Presentaciones", "scenarios": ["El escenario trata sobre saludar a alguien por primera vez", "El escenario trata sobre presentarse a uno mismo"]}, {"name": "Números y Colores", "scenarios": ["El escenario trata sobre contar del 1 al 10"]}]}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=200,
        finish_reason="stop",
        metadata={"completion_tokens": 150, "prompt_tokens": 50},
        created_at=datetime.now(),
    )

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are a curriculum generator...",  # create_system
        "Course description: Curso de Spanish nivel A1. sobre los siguientes temas: greetings, numbers.",  # create_user
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "submodules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "scenarios": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },  # create_response_schema
    ]

    mock_llm_adapter.generate_response.return_value = expected_llm_response

    request_data = {
        "level": "A1",
        "language": "Spanish",
        "topics": ["greetings", "numbers"],
    }

    # Act
    response = client.post(
        "/api/v1/curriculum/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "curriculum" in data
    assert "metadata" in data
    assert data["curriculum"]["name"] == "Curso de Español Básico"
    assert len(data["curriculum"]["submodules"]) == 2
    assert data["metadata"]["provider"] == "openai"
    assert data["metadata"]["tokens_used"] == 200

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_create_curriculum_without_topics(client):
    """Test: crear currículo sin topics."""
    # Arrange
    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    expected_llm_response = LLMResponse(
        content='{"name": "Intermediate English", "description": "Intermediate level English course", "submodules": []}',
        provider="openai",
        model="gpt-4o-mini",
        tokens_used=100,
        finish_reason="stop",
        metadata={},
        created_at=datetime.now(),
    )

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are a curriculum generator...",  # create_system
        "Course description: Curso de English nivel B1.",  # create_user
        {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "submodules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "scenarios": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },  # create_response_schema
    ]

    mock_llm_adapter.generate_response.return_value = expected_llm_response

    request_data = {
        "level": "B1",
        "language": "English",
    }

    # Act
    response = client.post(
        "/api/v1/curriculum/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["curriculum"]["name"] == "Intermediate English"

    # Verificar que se llamó al LLM mockeado
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_create_curriculum_missing_api_key():
    """Test: crear currículo sin API key."""
    from unittest.mock import AsyncMock, MagicMock

    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.interfaces.api.main import create_app

    # Crear un cliente sin override de verify_token para este test
    app = create_app()
    original_api_key = settings.api_key
    settings.api_key = "valid_key"

    # Mockear el use case para evitar llamadas reales
    mock_use_case = MagicMock()
    mock_use_case.execute = AsyncMock()

    use_case_dep = Provide[Container.generate_curriculum_use_case]
    app.dependency_overrides[use_case_dep] = lambda: mock_use_case

    test_client = TestClient(app)

    try:
        # Arrange
        request_data = {
            "level": "A1",
            "language": "Spanish",
        }

        # Act
        response = test_client.post(
            "/api/v1/curriculum/create",
            json=request_data,
            # No incluir header X-API-Key
        )

        # Assert
        assert response.status_code == 422  # FastAPI valida headers requeridos
    finally:
        app.dependency_overrides.clear()
        settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_create_curriculum_invalid_api_key():
    """Test: crear currículo con API key inválida."""
    from unittest.mock import AsyncMock, MagicMock

    from dependency_injector.wiring import Provide

    from src.config import settings
    from src.container import Container
    from src.interfaces.api.main import create_app

    # Crear un cliente sin override de verify_token para este test
    original_api_key = settings.api_key
    settings.api_key = "correct_key"

    # Crear mocks
    mock_use_case = MagicMock()
    mock_use_case.execute = AsyncMock()

    app = create_app()

    # No hacer override de verify_token - dejar que valide normalmente según settings
    use_case_dep = Provide[Container.generate_curriculum_use_case]
    app.dependency_overrides[use_case_dep] = lambda: mock_use_case

    test_client = TestClient(app)

    try:
        request_data = {
            "level": "A1",
            "language": "Spanish",
        }

        # Act
        response = test_client.post(
            "/api/v1/curriculum/create",
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
async def test_create_curriculum_ai_error(client):
    """Test: manejar error del proveedor de IA."""
    # Arrange
    from src.domain.exceptions.ai_exceptions import AIProviderError

    mock_llm_adapter = client._mock_llm
    mock_prompt_manager = client._mock_prompt_manager

    # Mock de los prompts
    mock_prompt_manager.render.side_effect = [
        "You are a curriculum generator...",  # create_system
        "Course description: Curso de Spanish nivel A1.",  # create_user
        {
            "type": "object",
            "properties": {},
        },  # create_response_schema
    ]

    # Hacer que el LLM lance un error
    mock_llm_adapter.generate_response.side_effect = AIProviderError("Error del proveedor")

    request_data = {
        "level": "A1",
        "language": "Spanish",
    }

    # Act
    response = client.post(
        "/api/v1/curriculum/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 500
    assert "Error al generar currículo" in response.json()["detail"]

    # Verificar que se intentó llamar al LLM
    mock_llm_adapter.generate_response.assert_called_once()


@pytest.mark.asyncio
async def test_create_curriculum_validation_error(client):
    """Test: validación de campos requeridos."""
    # Arrange - falta el campo 'level'
    request_data = {
        "language": "Spanish",
    }

    # Act
    response = client.post(
        "/api/v1/curriculum/create",
        json=request_data,
        headers={"X-API-Key": "valid_key"},
    )

    # Assert
    assert response.status_code == 422  # Unprocessable Entity
