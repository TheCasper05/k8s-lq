# Arquitectura Multi-Proveedor - LingoBot

## 🎯 Resumen Ejecutivo

LingoBot implementa una **arquitectura hexagonal** que permite cambiar de proveedor de IA (LLM, TTS, STT) simplemente modificando variables de entorno, sin tocar el código de negocio.

### Proveedores Soportados

| Tipo | Proveedores Disponibles |
|------|------------------------|
| **LLM** | OpenAI (GPT-4o-mini), Grok (X.AI) |
| **TTS** | OpenAI (tts-1), Eleven Labs (Multilingual v2) |
| **STT** | OpenAI (Whisper), Eleven Labs (Scribe v2 Realtime) |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                     │
│                   (Use Cases / Business Logic)           │
│                                                          │
│  GenerateTextResponseUseCase, ProcessAudioUseCase...   │
└──────────────────┬───────────────────────────────────────┘
                   │ depends on
                   ↓
┌─────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                         │
│                    (Ports / Interfaces)                  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ LLMPort  │  │ TTSPort  │  │ STTPort  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────┬───────────────────────────────────────┘
                   │ implemented by
                   ↓
┌─────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                     │
│                  (Adapters / Implementations)            │
│                                                          │
│  OpenAI      Grok        Eleven Labs                    │
│  ┌───────┐  ┌───────┐   ┌──────────────┐              │
│  │  LLM  │  │  LLM  │   │  TTS + STT   │              │
│  └───────┘  └───────┘   └──────────────┘              │
└──────────────────┬───────────────────────────────────────┘
                   │ created by
                   ↓
┌─────────────────────────────────────────────────────────┐
│                    FACTORY PATTERN                       │
│              (AIProviderFactory)                         │
│                                                          │
│  create_llm_adapter(provider)                           │
│  create_tts_adapter(provider)                           │
│  create_stt_adapter(provider)                           │
└──────────────────┬───────────────────────────────────────┘
                   │ injected via
                   ↓
┌─────────────────────────────────────────────────────────┐
│            DEPENDENCY INJECTION CONTAINER                │
│                 (dependency-injector)                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Cambio de Proveedor

### Ejemplo: Cambiar de OpenAI a Grok

```bash
# Antes (.env)
BOT_LLM_PROVIDER=openai
BOT_OPENAI_API_KEY=sk-abc123

# Después (.env)
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-xyz789
```

**Resultado**: Todo el código sigue funcionando sin cambios. El factory automáticamente crea el adaptador correcto.

---

## 📋 Implementaciones Actuales

### 1. LLM Adapters

#### OpenAI LLM Adapter
- **Archivo**: [src/infrastructure/adapters/ai/openai/openai_llm_adapter.py](../src/infrastructure/adapters/ai/openai/openai_llm_adapter.py)
- **Características**:
  - Generación de texto con GPT-4o-mini
  - Soporte para JSON mode
  - Function calling
  - Streaming (preparado)

#### Grok LLM Adapter
- **Archivo**: [src/infrastructure/adapters/ai/grok/grok_llm_adapter.py](../src/infrastructure/adapters/ai/grok/grok_llm_adapter.py)
- **Características**:
  - Compatible con API de OpenAI
  - Acceso a datos de X/Twitter
  - JSON mode
  - Base URL configurable

### 2. TTS Adapters

#### Eleven Labs TTS Adapter
- **Archivo**: [src/infrastructure/adapters/ai/elevenlabs/elevenlabs_tts_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_tts_adapter.py)
- **Características**:
  - TTS de alta calidad
  - Voces multiidioma
  - Control de stability, similarity_boost, style
  - Soporte para múltiples formatos (mp3, wav, ogg)
  - Listado de voces disponibles

### 3. STT Adapters

#### Eleven Labs STT Adapter (Scribe v2 Realtime)
- **Archivo**: [src/infrastructure/adapters/ai/elevenlabs/elevenlabs_stt_adapter.py](../src/infrastructure/adapters/ai/elevenlabs/elevenlabs_stt_adapter.py)
- **Características**:
  - Transcripción en tiempo real
  - Alta precisión
  - Detección automática de idioma
  - Soporte para 9+ formatos de audio
  - Optimizado para streaming

---

## 🎮 Casos de Uso

### Uso 1: Aplicación Básica con OpenAI

```env
BOT_LLM_PROVIDER=openai
BOT_TTS_PROVIDER=openai
BOT_STT_PROVIDER=openai
BOT_OPENAI_API_KEY=sk-...
```

**Ventaja**: Todo con un solo proveedor, configuración simple.

### Uso 2: Calidad Premium con Eleven Labs

```env
BOT_LLM_PROVIDER=openai
BOT_TTS_PROVIDER=elevenlabs  # Audio de alta calidad
BOT_STT_PROVIDER=elevenlabs  # Scribe v2 realtime
BOT_OPENAI_API_KEY=sk-...
BOT_ELEVENLABS_API_KEY=...
```

**Ventaja**: Mejor calidad de audio para podcasts, audiolibros, asistentes premium.

### Uso 3: Análisis de Social Media con Grok

```env
BOT_LLM_PROVIDER=grok        # Acceso a datos de X/Twitter
BOT_TTS_PROVIDER=elevenlabs
BOT_STT_PROVIDER=elevenlabs
BOT_GROK_API_KEY=xai-...
BOT_ELEVENLABS_API_KEY=...
```

**Ventaja**: LLM optimizado para análisis de redes sociales.

---

## 🔧 Componentes Clave

### 1. Factory Pattern ([factory.py](../src/infrastructure/adapters/ai/factory.py))

```python
class AIProviderFactory:
    def create_llm_adapter(self, provider: str | None = None) -> LLMPort:
        provider = provider or self.settings.llm_provider

        if provider == "openai":
            return OpenAILLMAdapter(...)
        elif provider == "grok":
            return GrokLLMAdapter(...)
        # ...
```

**Responsabilidad**: Crear instancias de adaptadores según configuración.

### 2. Ports ([src/domain/ports/ai/](../src/domain/ports/ai/))

```python
class LLMPort(ABC):
    @abstractmethod
    async def generate_response(...) -> LLMResponse:
        pass
```

**Responsabilidad**: Definir contratos que todos los adaptadores deben cumplir.

### 3. Container ([container.py](../src/container.py))

```python
class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Settings)
    ai_factory = providers.Singleton(AIProviderFactory, settings=config)
    llm_adapter = providers.Factory(
        lambda factory: factory.create_llm_adapter(),
        factory=ai_factory
    )
```

**Responsabilidad**: Inyección de dependencias y wiring de componentes.

---

## 🎓 Ventajas de Esta Arquitectura

### 1. **Flexibilidad Total**
Cambiar de proveedor no requiere cambios en el código:
```bash
# De OpenAI a Grok
sed -i 's/openai/grok/g' .env
```

### 2. **Testabilidad**
Mockear providers es trivial:
```python
mock_llm = MagicMock(spec=LLMPort)
use_case = GenerateTextResponseUseCase(llm=mock_llm)
```

### 3. **Aislamiento**
Cada proveedor está completamente aislado:
```
src/infrastructure/adapters/ai/
├── openai/
│   └── openai_llm_adapter.py
├── grok/
│   └── grok_llm_adapter.py
└── elevenlabs/
    ├── elevenlabs_tts_adapter.py
    └── elevenlabs_stt_adapter.py
```

### 4. **Extensibilidad**
Agregar un nuevo proveedor no afecta código existente:
- Crear adaptador
- Registrar en factory
- Actualizar config
- ¡Listo!

### 5. **Configuración Centralizada**
Todo se controla desde `.env`:
```env
BOT_LLM_PROVIDER=openai
BOT_TTS_PROVIDER=elevenlabs
BOT_STT_PROVIDER=elevenlabs
```

---

## 📚 Documentación Relacionada

- **[AGREGAR_PROVEEDORES.md](./AGREGAR_PROVEEDORES.md)**: Guía paso a paso para agregar nuevos proveedores
- **[EJEMPLOS_PROVEEDORES.md](./EJEMPLOS_PROVEEDORES.md)**: Ejemplos de código usando diferentes proveedores
- **[EJEMPLO_USO.md](./EJEMPLO_USO.md)**: Guía de uso general del sistema
- **[CLAUDE.md](../CLAUDE.md)**: Documentación completa del proyecto

---

## 🧪 Testing

Todos los tests siguen pasando independientemente del proveedor configurado:

```bash
uv run pytest tests/ -v
# ====== 12 passed in 0.18s ======
```

Los tests usan **mocks** para no depender de APIs reales:

```python
@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.generate_response = AsyncMock()
    return llm
```

---

## 🚀 Próximos Pasos

1. ✅ Implementar adaptadores TTS/STT de OpenAI
2. ✅ Crear casos de uso para audio (STT → LLM → TTS)
3. ✅ Endpoints de API para procesar audio
4. ⬜ Tests de integración con APIs reales (opcional)
5. ⬜ Sistema de caché para reducir costos
6. ⬜ Métricas y monitoring por proveedor

---

## 🎯 Conclusión

Esta arquitectura permite a LingoBot:
- **Experimentar** con diferentes proveedores fácilmente
- **Optimizar costos** usando el proveedor más económico para cada tarea
- **Mejorar calidad** usando proveedores especializados (Eleven Labs para audio)
- **Reducir riesgo** no dependiendo de un solo proveedor
- **Escalar** agregando nuevos proveedores sin refactorizar

**Todo esto manteniendo la simplicidad del código de negocio.**
