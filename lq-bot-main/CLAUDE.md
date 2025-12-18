# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LingoBot is a FastAPI service for LingoQuesto that processes HTTP requests and returns AI-generated audio and responses. The project implements **Hexagonal Architecture** (Ports and Adapters pattern) to keep business logic independent from frameworks, databases, and external services.

## Commands

### Development Workflow
```bash
# Initial setup
make init                # Create venv and install all dependencies

# Development cycle
make dev                 # Run format + lint + test + start server
make qa                  # Run format + lint + test (without starting server)
make run                 # Start development server with auto-reload

# Individual tasks
make test                # Run pytest
make lint                # Run ruff linter
make format              # Format code with ruff
make check               # Run lint + test (without formatting)

# Testing
uv run pytest                    # Run all tests
uv run pytest tests/test_foo.py  # Run specific test file
uv run pytest -k test_name       # Run tests matching pattern

# Cleanup
make clean               # Remove cache and temp files
make reset-venv          # Clean, clear uv cache, and reinstall dependencies
```

### Running the Application
The main entry point is at [src/interfaces/api/main.py](src/interfaces/api/main.py). The app runs on `http://localhost:8081` with:
- Swagger UI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`

## Architecture

### Hexagonal Architecture Layers

The codebase strictly follows hexagonal architecture with clear separation:

1. **Domain** ([src/domain/](src/domain/)) - Core business logic, zero external dependencies
   - [models/](src/domain/models/) - Pure domain entities (Message, Audio, etc.)
   - [ports/](src/domain/ports/) - Abstract interfaces defining contracts (LLMPort, TTSPort, STTPort, etc.)
   - [services/](src/domain/services/) - Domain services containing business logic
   - [exceptions/](src/domain/exceptions/) - Domain-specific exceptions

2. **Application** ([src/application/](src/application/)) - Use case orchestration
   - [use_cases/](src/application/use_cases/) - Application-specific business flows

3. **Infrastructure** ([src/infrastructure/](src/infrastructure/)) - Concrete implementations
   - [adapters/ai/](src/infrastructure/adapters/ai/) - AI provider implementations (OpenAI, Anthropic, Google)
   - [repositories/](src/infrastructure/repositories/) - Data persistence implementations
   - [logging/](src/infrastructure/logging/) - Logging infrastructure

4. **Interfaces** ([src/interfaces/](src/interfaces/)) - External-facing adapters
   - [api/](src/interfaces/api/) - FastAPI routes and middleware
   - [api/v1/](src/interfaces/api/v1/) - API v1 endpoints

### Dependency Injection

The project uses `dependency-injector` with a centralized container pattern in [src/container.py](src/container.py):

```python
# Container wires together:
# Settings -> AIProviderFactory -> Adapters (LLM/TTS/STT) -> Services
```

When adding new services or adapters:
1. Define the port (interface) in [src/domain/ports/](src/domain/ports/)
2. Implement the adapter in [src/infrastructure/adapters/](src/infrastructure/adapters/)
3. Register both in [src/container.py](src/container.py)
4. Inject into services/use cases through constructor

### AI Provider Abstraction

AI services (LLM, TTS, STT) are abstracted through ports, permitiendo cambiar de proveedor sin modificar la lógica de negocio:

- **Ports** define interfaces: [src/domain/ports/ai/](src/domain/ports/ai/)
- **Factory** creates providers: [src/infrastructure/adapters/ai/factory.py](src/infrastructure/adapters/ai/factory.py)
- **Providers soportados**:
  - **LLM**: OpenAI, Grok (X.AI)
  - **TTS**: OpenAI, Eleven Labs
  - **STT**: OpenAI (Whisper), Eleven Labs (Scribe v2 Realtime)

**Cambiar de proveedor es tan simple como cambiar una variable de entorno:**

```env
# Usar Grok en lugar de OpenAI
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-tu-key
```

**Agregar un nuevo proveedor:**
1. Implementar el port interface (LLMPort/TTSPort/STTPort)
2. Registrar en AIProviderFactory
3. Actualizar configuración en [src/config.py](src/config.py)
4. Ver guía detallada: [docs/AGREGAR_PROVEEDORES.md](docs/AGREGAR_PROVEEDORES.md)

## Configuration

Settings use `pydantic-settings` with configuration in [src/config.py](src/config.py):

```env
# Environment variables use BOT_ prefix:
BOT_LLM_PROVIDER=openai
BOT_OPENAI_API_KEY=sk-...
BOT_OPENAI_LLM_MODEL=gpt-4o-mini

# O usar Grok:
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-...
BOT_GROK_LLM_MODEL=grok-beta

# Eleven Labs para STT:
BOT_STT_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=...
BOT_ELEVENLABS_STT_MODEL=scribe-v2-realtime
```

All settings are loaded from `.env` file (see [.env.example](.env.example)).

**Documentación de proveedores:**
- [Guía para agregar proveedores](docs/AGREGAR_PROVEEDORES.md)
- [Ejemplos de uso](docs/EJEMPLOS_PROVEEDORES.md)

## Code Style

- **Linting/Formatting**: Ruff ([ruff.toml](ruff.toml))
  - Line length: 100 characters
  - Target: Python 3.11+
  - Auto-fix enabled
  - Import sorting with isort
- **Type Checking**: mypy configured for strict mode in [pyproject.toml](pyproject.toml)
- **Testing**: pytest with async support

## Important Patterns

### Dependency Flow (Dependency Inversion)
- Domain layer defines interfaces (ports) but knows nothing about implementations
- Infrastructure layer depends on domain interfaces, not vice versa
- Never import from infrastructure into domain

### Service Pattern
Domain services (like [ConversationService](src/domain/services/conversation_service.py)) receive ports via constructor:
```python
class ConversationService:
    def __init__(self, llm: LLMPort, tts: TTSPort, stt: STTPort):
        # Business logic uses ports, not concrete implementations
```

### Route Organization
API routes are versioned under [src/interfaces/api/v1/](src/interfaces/api/v1/) and should:
- Use FastAPI dependency injection for services
- Keep controllers thin (delegate to use cases/services)
- Return proper HTTP status codes and response models

## Project Status

Currently implemented:
- ✅ Base hexagonal architecture structure
- ✅ FastAPI setup with health check endpoint
- ✅ Configuration system with pydantic-settings (multi-provider support)
- ✅ AI provider abstraction with multiple providers:
  - LLM: OpenAI, Grok (X.AI)
  - TTS: OpenAI, Eleven Labs
  - STT: OpenAI (Whisper), Eleven Labs (Scribe v2)
- ✅ Dependency injection container (dependency-injector)
- ✅ Complete use case: GenerateTextResponseUseCase
- ✅ API endpoint: POST /api/v1/chat/generate
- ✅ Testing framework (12 tests passing: unit + integration)

Pending implementation:
- Use cases for audio processing workflows (TTS/STT)
- API endpoints for audio generation
- Storage repositories
- Production logging and monitoring
