# Guía: Cómo Agregar Nuevos Proveedores de IA

Esta guía explica paso a paso cómo agregar nuevos proveedores de IA (LLM, TTS, STT) a LingoBot manteniendo la arquitectura hexagonal.

## Índice

1. [Arquitectura](#arquitectura)
2. [Agregar un Proveedor LLM](#agregar-un-proveedor-llm)
3. [Agregar un Proveedor TTS](#agregar-un-proveedor-tts)
4. [Agregar un Proveedor STT](#agregar-un-proveedor-stt)
5. [Ejemplos Completos](#ejemplos-completos)

---

## Arquitectura

La arquitectura hexagonal nos permite agregar nuevos proveedores fácilmente:

```
Domain (Ports/Interfaces)
    ↓
Infrastructure (Adapters/Implementations)
    ↓
Factory (Crea instancias según configuración)
    ↓
Container (Inyección de dependencias)
```

**Ventaja**: Puedes cambiar de proveedor simplemente cambiando una variable de entorno, sin modificar la lógica de negocio.

---

## Agregar un Proveedor LLM

### Paso 1: Definir Configuración

Edita [src/config.py](../src/config.py):

```python
class Settings(BaseSettings):
    # ... código existente ...

    # Proveedor por defecto
    llm_provider: str = Field(default="openai", description="...")

    # Configuración específica del nuevo proveedor
    mi_proveedor_api_key: str = Field(default="", description="API Key de MiProveedor")
    mi_proveedor_llm_model: str = Field(default="modelo-v1", description="Modelo LLM")
    mi_proveedor_base_url: str = Field(default="https://api.example.com", description="URL base")
```

### Paso 2: Crear el Adaptador

Crea `src/infrastructure/adapters/ai/mi_proveedor/mi_proveedor_llm_adapter.py`:

```python
"""Adaptador LLM para MiProveedor."""

from datetime import datetime
from typing import Any

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.message import LLMResponse, Message
from src.domain.ports.ai.llm_port import LLMPort


class MiProveedorLLMAdapter(LLMPort):
    """Implementación del port LLM usando MiProveedor."""

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.provider_name = "mi_proveedor"

    async def generate_response(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_schema: dict[str, Any] | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Genera respuesta usando la API de MiProveedor."""
        try:
            # 1. Convertir mensajes de dominio al formato de la API
            api_messages = self._convert_messages(messages, system_prompt)

            # 2. Hacer request a la API (usa httpx, requests, o SDK específico)
            # ... tu código de integración ...

            # 3. Convertir respuesta al modelo de dominio
            return LLMResponse(
                content="respuesta del modelo",
                provider=self.provider_name,
                model=self.model,
                tokens_used=100,
                finish_reason="stop",
                metadata={},
                created_at=datetime.now(),
            )

        except Exception as e:
            raise AIProviderError(
                f"Error en {self.provider_name}: {e!s}",
                provider=self.provider_name,
                original_error=e,
            ) from e

    async def generate_structured_response(
        self,
        messages: list[Message],
        response_format: dict[str, Any],
        system_prompt: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Implementa generación estructurada si el proveedor lo soporta."""
        # Implementación específica
        pass

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": ["text_generation"],
        }

    def _convert_messages(
        self, messages: list[Message], system_prompt: str | None = None
    ) -> list[dict]:
        """Convierte mensajes de dominio al formato de la API."""
        # Implementación específica del formato del proveedor
        pass
```

### Paso 3: Registrar en el Factory

Edita [src/infrastructure/adapters/ai/factory.py](../src/infrastructure/adapters/ai/factory.py):

```python
def create_llm_adapter(self, provider: str | None = None) -> LLMPort:
    provider = provider or self.settings.llm_provider

    if provider == "openai":
        # ... código existente ...

    elif provider == "mi_proveedor":
        from src.infrastructure.adapters.ai.mi_proveedor.mi_proveedor_llm_adapter import (
            MiProveedorLLMAdapter,
        )

        return MiProveedorLLMAdapter(
            api_key=self.settings.mi_proveedor_api_key,
            model=self.settings.mi_proveedor_llm_model,
            base_url=self.settings.mi_proveedor_base_url,
        )

    else:
        raise ValueError(
            f"Proveedor LLM '{provider}' no soportado. "
            f"Proveedores disponibles: openai, grok, mi_proveedor"
        )
```

### Paso 4: Actualizar .env.example

```env
# Mi Proveedor LLM
BOT_MI_PROVEEDOR_API_KEY=tu-api-key
BOT_MI_PROVEEDOR_LLM_MODEL=modelo-v1
BOT_MI_PROVEEDOR_BASE_URL=https://api.example.com
```

### Paso 5: Usar el Nuevo Proveedor

```bash
# En tu archivo .env
BOT_LLM_PROVIDER=mi_proveedor
BOT_MI_PROVEEDOR_API_KEY=tu-api-key-real
```

¡Listo! Ahora tu aplicación usará el nuevo proveedor automáticamente.

---

## Agregar un Proveedor TTS

Similar a LLM, pero implementando [TTSPort](../src/domain/ports/ai/tts_port.py):

### Métodos Requeridos

```python
class MiProveedorTTSAdapter(TTSPort):
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
        audio_format: Literal["wav", "mp3", "ogg"] = "wav",
        speed: float = 1.0,
        **kwargs,
    ) -> AudioOutput:
        """Convierte texto a audio."""
        # Tu implementación
        pass

    async def get_available_voices(
        self, language: str | None = None
    ) -> list[VoiceConfig]:
        """Lista las voces disponibles."""
        # Tu implementación
        pass

    def get_provider_name(self) -> str:
        return "mi_proveedor_tts"
```

Ver ejemplo completo en [elevenlabs_tts_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_tts_adapter.py)

---

## Agregar un Proveedor STT

Implementa [STTPort](../src/domain/ports/ai/stt_port.py):

### Métodos Requeridos

```python
class MiProveedorSTTAdapter(STTPort):
    async def transcribe_audio(
        self,
        audio: bytes | Path,
        language: str | None = None,
        temperature: float = 0.0,
        **kwargs,
    ) -> TranscriptionResult:
        """Transcribe audio a texto."""
        # Tu implementación
        pass

    async def translate_audio(
        self, audio: bytes | Path, target_language: str = "en", **kwargs
    ) -> TranscriptionResult:
        """Transcribe y traduce audio."""
        # Tu implementación
        pass

    def get_supported_formats(self) -> list[str]:
        return ["mp3", "wav", "ogg"]

    def get_provider_name(self) -> str:
        return "mi_proveedor_stt"
```

Ver ejemplo completo en [elevenlabs_stt_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_stt_adapter.py)

---

## Ejemplos Completos

### Ejemplo 1: Grok (X.AI) como LLM

```bash
# .env
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-tu-api-key
BOT_GROK_LLM_MODEL=grok-beta
```

Ver implementación: [grok_llm_adapter.py](../src/infrastructure/adapters/ai/grok/grok_llm_adapter.py)

### Ejemplo 2: Eleven Labs como STT

```bash
# .env
BOT_STT_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key
BOT_ELEVENLABS_STT_MODEL=scribe-v2-realtime
```

Ver implementación: [elevenlabs_stt_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_stt_adapter.py)

### Ejemplo 3: Eleven Labs como TTS

```bash
# .env
BOT_TTS_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key
BOT_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

Ver implementación: [elevenlabs_tts_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_tts_adapter.py)

---

## Checklist de Implementación

Cuando agregues un nuevo proveedor, verifica:

- [ ] ✅ Configuración añadida en `config.py`
- [ ] ✅ Adaptador creado implementando el Port correspondiente
- [ ] ✅ Adaptador registrado en `factory.py`
- [ ] ✅ Variables añadidas a `.env.example`
- [ ] ✅ Manejo de errores con `AIProviderError`
- [ ] ✅ Conversión correcta entre modelos de dominio y API
- [ ] ✅ Tests unitarios para el adaptador (opcional pero recomendado)
- [ ] ✅ Documentación actualizada

---

## Ventajas de Esta Arquitectura

1. **Flexibilidad**: Cambia de proveedor sin cambiar código de negocio
2. **Testabilidad**: Mock fácilmente los proveedores en tests
3. **Extensibilidad**: Agrega proveedores sin modificar código existente
4. **Aislamiento**: Cada proveedor está aislado en su propio módulo
5. **Configuración**: Todo se controla mediante variables de entorno

---

## Preguntas Frecuentes

### ¿Puedo usar múltiples proveedores simultáneamente?

Sí, puedes crear instancias específicas:

```python
# En tu código
from src.container import Container

container = Container()
factory = container.ai_factory()

# Obtener diferentes proveedores
openai_llm = factory.create_llm_adapter("openai")
grok_llm = factory.create_llm_adapter("grok")
```

### ¿Cómo agrego dependencias extra (ej: SDK específico)?

Agrega la dependencia en `pyproject.toml`:

```toml
dependencies = [
  # ... existentes ...
  "mi-sdk-provider>=1.0.0",
]
```

Luego ejecuta:

```bash
uv sync
```

### ¿Dónde pongo la lógica específica del proveedor?

Siempre en el adaptador. El adaptador es responsable de:
- Convertir entre modelos de dominio y formato de la API
- Manejar autenticación
- Gestionar rate limits
- Convertir errores de la API a `AIProviderError`

---

## Recursos

- [OpenAI LLM Adapter](../src/infrastructure/adapters/ai/openai/openai_llm_adapter.py)
- [Grok LLM Adapter](../src/infrastructure/adapters/ai/grok/grok_llm_adapter.py)
- [Eleven Labs STT Adapter](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_stt_adapter.py)
- [Eleven Labs TTS Adapter](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_tts_adapter.py)
