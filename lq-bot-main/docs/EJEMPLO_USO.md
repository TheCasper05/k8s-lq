# Ejemplo de Uso - LingoBot

Este documento muestra cómo usar el caso de uso implementado y el endpoint de la API.

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto:

```env
BOT_APP_NAME=lq-bot
BOT_ENVIRONMENT=local
BOT_LOG_LEVEL=INFO

# OpenAI Configuration (requerido para usar la API)
BOT_OPENAI_API_KEY=sk-tu-api-key-aqui
BOT_OPENAI_LLM_MODEL=gpt-4o-mini
```

## Ejecutar la Aplicación

```bash
# Opción 1: Usando make
make run

# Opción 2: Usando uvicorn directamente
uv run uvicorn src.interfaces.api.main:app --reload --host 0.0.0.0 --port 8081
```

La aplicación estará disponible en `http://localhost:8081`

## Endpoints Disponibles

### Health Check

```bash
curl http://localhost:8081/health
```

**Respuesta:**
```json
{
  "status": "ok"
}
```

### Generar Respuesta de Texto

```bash
curl -X POST http://localhost:8081/api/v1/chat/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, ¿cómo estás?",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

**Respuesta:**
```json
{
  "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte hoy?",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 35,
  "finish_reason": "stop"
}
```

### Con System Prompt

```bash
curl -X POST http://localhost:8081/api/v1/chat/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Traduce al inglés: Hola mundo",
    "system_prompt": "Eres un traductor profesional de español a inglés.",
    "temperature": 0.3,
    "max_tokens": 500
  }'
```

## Uso Programático (Python)

### Desde Código Python

```python
import asyncio
from src.container import Container
from src.application.use_cases.generate_text_response_use_case import GenerateTextResponseUseCase

async def main():
    # Inicializar container
    container = Container()

    # Obtener el caso de uso
    use_case: GenerateTextResponseUseCase = container.generate_text_response_use_case()

    # Ejecutar
    response = await use_case.execute(
        user_message="¿Cuál es la capital de Francia?",
        system_prompt="Eres un asistente educativo.",
        temperature=0.7,
        max_tokens=1000
    )

    print(f"Respuesta: {response.content}")
    print(f"Tokens usados: {response.tokens_used}")
    print(f"Modelo: {response.model}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentación Interactiva

Una vez que la aplicación esté corriendo, puedes acceder a:

- **Swagger UI**: http://localhost:8081/docs
- **ReDoc**: http://localhost:8081/redoc

Estas interfaces te permiten probar los endpoints directamente desde el navegador.

## Tests

```bash
# Ejecutar todos los tests
make test

# O con pytest directamente
uv run pytest tests/ -v

# Solo tests unitarios
uv run pytest tests/unit/ -v

# Solo tests de integración
uv run pytest tests/integration/ -v

# Con coverage
uv run pytest tests/ --cov=src --cov-report=html
```

## Estructura del Caso de Uso

El caso de uso `GenerateTextResponseUseCase` sigue el patrón de arquitectura hexagonal:

1. **Entrada**: Recibe un mensaje de usuario y parámetros opcionales
2. **Procesamiento**: Usa el puerto `LLMPort` para generar la respuesta
3. **Salida**: Retorna un `LLMResponse` con la respuesta y metadata

Este diseño permite:
- Testear sin dependencias externas (usando mocks)
- Cambiar el proveedor de IA sin modificar el caso de uso
- Reutilizar la lógica desde diferentes interfaces (API, CLI, etc.)
