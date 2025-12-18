# Ejemplos de Uso: Múltiples Proveedores de IA

Este documento muestra cómo usar los diferentes proveedores de IA implementados.

## Configuración Rápida

### Opción 1: OpenAI (Por defecto)

```env
# .env
BOT_LLM_PROVIDER=openai
BOT_OPENAI_API_KEY=sk-tu-api-key-aqui
BOT_OPENAI_LLM_MODEL=gpt-4o-mini
```

### Opción 2: Grok (X.AI)

```env
# .env
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-tu-api-key-aqui
BOT_GROK_LLM_MODEL=grok-beta
BOT_GROK_BASE_URL=https://api.x.ai/v1
```

### Opción 3: Eleven Labs STT

```env
# .env
BOT_STT_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key-aqui
BOT_ELEVENLABS_STT_MODEL=scribe-v2-realtime
BOT_ELEVENLABS_STT_LANGUAGE=en
```

### Opción 4: Eleven Labs TTS

```env
# .env
BOT_TTS_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key-aqui
BOT_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
BOT_ELEVENLABS_TTS_MODEL=eleven_multilingual_v2
```

---

## Ejemplo 1: Usar Grok como LLM

### Configuración

```env
BOT_LLM_PROVIDER=grok
BOT_GROK_API_KEY=xai-abc123...
BOT_GROK_LLM_MODEL=grok-beta
```

### Código Python

```python
from src.container import Container

# El container automáticamente usa Grok según la configuración
container = Container()
use_case = container.generate_text_response_use_case()

response = await use_case.execute(
    user_message="¿Cuál es la capital de Francia?",
    temperature=0.7
)

print(f"Proveedor: {response.provider}")  # "grok"
print(f"Respuesta: {response.content}")
```

### Via API

```bash
# La API automáticamente usa el proveedor configurado
curl -X POST http://localhost:8081/api/v1/chat/generate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explícame la teoría de la relatividad"
  }'
```

---

## Ejemplo 2: Usar Eleven Labs para STT

### Configuración

```env
BOT_STT_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key
BOT_ELEVENLABS_STT_MODEL=scribe-v2-realtime
```

### Código Python

```python
from pathlib import Path
from src.container import Container

container = Container()
factory = container.ai_factory()

# Crear adaptador STT de Eleven Labs
stt = factory.create_stt_adapter("elevenlabs")

# Transcribir audio
audio_path = Path("audio.mp3")
result = await stt.transcribe_audio(
    audio=audio_path,
    language="es"
)

print(f"Texto: {result.text}")
print(f"Idioma detectado: {result.language}")
print(f"Confianza: {result.confidence}")
```

### Formatos Soportados

```python
# Eleven Labs STT soporta múltiples formatos
formats = stt.get_supported_formats()
print(formats)
# ['mp3', 'wav', 'flac', 'ogg', 'm4a', 'webm', 'mp4', 'mpeg', 'mpga']
```

---

## Ejemplo 3: Usar Eleven Labs para TTS

### Configuración

```env
BOT_TTS_PROVIDER=elevenlabs
BOT_ELEVENLABS_API_KEY=tu-api-key
BOT_ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### Código Python

```python
from src.container import Container

container = Container()
factory = container.ai_factory()

# Crear adaptador TTS de Eleven Labs
tts = factory.create_tts_adapter("elevenlabs")

# Sintetizar voz
audio = await tts.synthesize_speech(
    text="Hola, esto es una prueba de Eleven Labs TTS",
    voice="default",  # Usa la voz configurada
    language="es",
    audio_format="mp3",
)

# Guardar audio
with open("output.mp3", "wb") as f:
    f.write(audio.audio_data)

print(f"Audio generado: {audio.duration_seconds}s")
print(f"Formato: {audio.format}")
```

### Listar Voces Disponibles

```python
# Obtener todas las voces disponibles
voices = await tts.get_available_voices()

for voice in voices:
    print(f"- {voice.name} ({voice.id})")
    print(f"  Idioma: {voice.language}")
    print(f"  Género: {voice.gender}")
```

### Parámetros Avanzados

```python
# Control fino de la voz
audio = await tts.synthesize_speech(
    text="Texto con emoción",
    voice="21m00Tcm4TlvDq8ikWAM",
    stability=0.5,           # Control de estabilidad (0-1)
    similarity_boost=0.75,   # Similitud con voz original (0-1)
    style=0.3,               # Estilo/expresividad
    use_speaker_boost=True,  # Mejora de claridad
)
```

---

## Ejemplo 4: Combinar Múltiples Proveedores

```python
from src.container import Container

container = Container()
factory = container.ai_factory()

# Usar OpenAI para LLM
llm = factory.create_llm_adapter("openai")

# Usar Eleven Labs para TTS
tts = factory.create_tts_adapter("elevenlabs")

# Usar Eleven Labs para STT
stt = factory.create_stt_adapter("elevenlabs")

# Flujo completo: Audio → Texto → LLM → Audio
async def process_voice_message(audio_file: Path):
    # 1. Transcribir audio con Eleven Labs
    transcription = await stt.transcribe_audio(audio_file)
    print(f"Usuario dijo: {transcription.text}")

    # 2. Generar respuesta con OpenAI
    from src.domain.models.message import Message
    from datetime import datetime

    user_msg = Message(
        role="user",
        content=transcription.text,
        timestamp=datetime.now()
    )

    llm_response = await llm.generate_response(
        messages=[user_msg],
        system_prompt="Eres un asistente amigable",
        temperature=0.7
    )
    print(f"IA responde: {llm_response.content}")

    # 3. Convertir respuesta a audio con Eleven Labs
    audio_response = await tts.synthesize_speech(
        text=llm_response.content,
        voice="default",
        language="es"
    )

    # 4. Guardar audio de respuesta
    with open("response.mp3", "wb") as f:
        f.write(audio_response.audio_data)

    return llm_response.content

# Usar
await process_voice_message(Path("user_audio.mp3"))
```

---

## Ejemplo 5: Cambiar Proveedores Dinámicamente

```python
from src.container import Container

container = Container()
factory = container.ai_factory()

# Probar con diferentes proveedores LLM
providers = ["openai", "grok"]
user_message = "¿Cuál es la capital de España?"

for provider in providers:
    llm = factory.create_llm_adapter(provider)

    response = await llm.generate_response(
        messages=[Message(
            role="user",
            content=user_message,
            timestamp=datetime.now()
        )],
        temperature=0.7
    )

    print(f"\n[{provider.upper()}] {response.content}")
    print(f"Tokens: {response.tokens_used}")
```

---

## Ejemplo 6: Manejo de Errores

```python
from src.domain.exceptions.ai_exceptions import AIProviderError

try:
    llm = factory.create_llm_adapter("grok")
    response = await llm.generate_response(
        messages=[user_message],
        temperature=0.7
    )
except AIProviderError as e:
    print(f"Error del proveedor {e.provider}: {e.message}")
    print(f"Error original: {e.original_error}")

    # Fallback a otro proveedor
    print("Intentando con OpenAI...")
    llm = factory.create_llm_adapter("openai")
    response = await llm.generate_response(
        messages=[user_message],
        temperature=0.7
    )
```

---

## Comparación de Proveedores

### LLM

| Proveedor | Ventajas | Casos de Uso |
|-----------|----------|--------------|
| **OpenAI** | Muy robusto, JSON mode, function calling | General, producción |
| **Grok** | Acceso a datos de X/Twitter, rápido | Social media, análisis |

### TTS

| Proveedor | Ventajas | Casos de Uso |
|-----------|----------|--------------|
| **OpenAI** | Económico, rápido | Aplicaciones básicas |
| **Eleven Labs** | Calidad superior, muy natural | Podcasts, audiolibros, asistentes premium |

### STT

| Proveedor | Ventajas | Casos de Uso |
|-----------|----------|--------------|
| **OpenAI Whisper** | Muy preciso, multiidioma | General, transcripciones |
| **Eleven Labs Scribe v2** | Tiempo real, alta precisión | Live streaming, llamadas |

---

## Recursos

- [Guía completa de cómo agregar proveedores](./AGREGAR_PROVEEDORES.md)
- [OpenAI API](https://platform.openai.com/docs)
- [Grok API](https://x.ai/api)
- [Eleven Labs API](https://elevenlabs.io/docs)
