# 🧩 Documentación de Endpoints para Migración

Guía completa y organizada por categorías, con títulos, descripciones, DTOs, casos de uso y pruebas sugeridas.

---

# 📊 1. Audio Processing (Speech-to-Text / Text-to-Speech)

## **1. POST /api/v1/audio/transcription**

**Descripción:**  
Transcribe un archivo de audio a texto usando el servicio STT configurado. Soporta múltiples formatos (.ogg de WhatsApp y otros).

**Request:**
- Form data con `multipart/form-data`:
  - `file`: Archivo de audio (UploadFile) - opcional si se proporciona `url`
  - `url`: URL del archivo de audio (string) - opcional si se proporciona `file`
  - `language`: Código de idioma (string, opcional) - auto-detect si no se proporciona

**Ejemplo con file:**
```bash
curl -X POST "http://localhost:8081/api/v1/audio/transcription" \
  -H "X-API-Key: your-api-key" \
  -F "file=@audio.mp3" \
  -F "language=en"
```

**Ejemplo con URL:**
```bash
curl -X POST "http://localhost:8081/api/v1/audio/transcription" \
  -H "X-API-Key: your-api-key" \
  -F "url=https://bucket.s3.amazonaws.com/audio.mp3" \
  -F "language=en"
```

**Response:**
```json
{
  "transcription": "Texto transcrito del audio",
  "provider": "openai",
  "model": "whisper-1"
}
```

**Características:**
- Acepta `file` (UploadFile) o `url` (string) - debe proporcionarse uno u otro, no ambos
- Si es `file` → lee directamente el archivo subido
- Si es `url` → detecta automáticamente si es S3/DigitalOcean Spaces o HTTP/HTTPS
- Si es URL S3/DigitalOcean → descarga mediante `storage_adapter` (boto3)
- Si es URL HTTP/HTTPS → descarga mediante httpx
- Valida `api_key` vía header `X-API-Key` usando `Depends(verify_token)`
- Usa `GenerateTranscriptionUseCase` para procesar el audio
- Maneja errores: `AIProviderError`, errores de descarga, formato inválido

**Status Codes:**
- `200 OK` - Transcripción exitosa
- `400 Bad Request` - Source inválido o error al descargar
- `401 Unauthorized` - API key inválida
- `422 Unprocessable Entity` - Error de validación
- `500 Internal Server Error` - Error del proveedor STT

**Tests:**
- Unitarios: `tests/unit/test_audio_transcription_endpoint.py`
- Integración: `tests/integration/test_audio_transcription_api.py`

---

## **2. POST /api/v1/audio/create_voice**

**Descripción:**  
Convierte texto a audio usando el servicio TTS configurado (MP3, OGG o WAV). Retorna un archivo de audio descargable.

**Request Body:**
```json
{
  "text": "Hello, this is a test",
  "voice": "alloy",
  "language": "en",
  "audio_format": "mp3",
  "speed": 1.0
}
```

**Campos:**
- `text` (requerido): Texto a convertir en audio (1-5000 caracteres)
- `voice` (opcional): ID de la voz a usar (default: "default")
- `language` (opcional): Código de idioma ISO 639-1 (default: "en")
- `audio_format` (opcional): Formato de audio - "mp3", "ogg" o "wav" (default: "mp3")
- `speed` (opcional): Velocidad de reproducción 0.25-4.0 (default: 1.0)

**Response:**
- Content-Type: `audio/mpeg`, `audio/ogg` o `audio/wav` según formato
- Headers:
  - `X-Audio-Duration`: Duración del audio en segundos
  - `X-Voice-Used`: Voz utilizada
  - `X-Provider`: Proveedor TTS usado
- Body: Archivo de audio binario

**Autenticación:**
- Requiere header `X-API-Key` con API key válida

**Errores:**
- `400`: Validación de request (texto vacío, formato inválido, etc.)
- `401`: API key inválida o no proporcionada
- `500`: Error al generar audio (AIProviderError)

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8081/api/v1/audio/create_voice" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "alloy", "audio_format": "mp3"}' \
  --output audio.mp3
```

---

## **3. POST /api/v1/audio/translate-native**

**Descripción:**  
Transcribe, traduce y sintetiza audio en una sola operación.

---

# 💬 2. Conversation & Chat

## **4. POST /api/v1/conversation/answer**

Genera una respuesta manteniendo una conversación multi-turno mediante `response_id`.

---

## **5. POST /api/v1/conversation/start**

Inicia una conversación y retorna audio de bienvenida.

---

## **6. POST /api/v1/conversation/suggestions**

Genera 3–5 sugerencias contextuales en una conversación.

---

# 🌍 3. Translation

## **7. POST /api/v1/translation/translations**

**Descripción:**  
Endpoint unificado y flexible que traduce mensajes simples o estructuras JSON según el tipo de entrada proporcionada.

**Request Body:**
```json
{
  "message_text": "Hello, how are you?",
  "target_language": "Spanish",
  "native_language": "English"
}
```

O para traducción batch:
```json
{
  "data": [
    {"id": "1", "word": "Hello"},
    {"id": "2", "word": "World"}
  ],
  "target_language": "Spanish",
  "native_language": "English"
}
```

**Campos:**
- `message_text` (string, opcional): Texto simple a traducir (requerido si no se proporciona `data`)
- `data` (array, opcional): Array de objetos JSON con `id` y texto a traducir (requerido si no se proporciona `message_text`)
- `target_language` (string, requerido): Idioma destino para la traducción
- `native_language` (string, opcional): Idioma nativo (para contexto)

**Validaciones:**
- Debe proporcionarse `message_text` o `data`, pero no ambos
- Cada elemento de `data` debe tener un campo `id` y al menos un campo de texto
- `target_language` es requerido

**Response para texto simple:**
```json
{
  "translation": "Hola, ¿cómo estás?",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 50
}
```

**Response para batch:**
```json
{
  "translations": [
    {"id": "1", "translation": "Hola"},
    {"id": "2", "translation": "Mundo"}
  ],
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 100
}
```

**Características:**
- Si se proporciona `message_text` → usa `TranslateMessageUseCase` para traducción simple
- Si se proporciona `data` → usa `BatchTranslateUseCase` para traducción batch con estructura JSON
- Valida `api_key` vía header `X-API-Key` usando `Depends(verify_token)`
- Devuelve traducción en el mismo formato que la entrada
- Soporta idioma nativo opcional para mejor contexto

**Status Codes:**
- `200 OK` - Traducción exitosa
- `400 Bad Request` - Validación de request (faltan campos, ambos inputs, etc.)
- `401 Unauthorized` - API key inválida
- `422 Unprocessable Entity` - Error de validación
- `500 Internal Server Error` - Error del proveedor LLM

**Ejemplo con texto simple:**
```bash
curl -X POST "http://localhost:8081/api/v1/translation/translations" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message_text": "Hello, how are you?",
    "target_language": "Spanish"
  }'
```

**Ejemplo con batch:**
```bash
curl -X POST "http://localhost:8081/api/v1/translation/translations" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"id": "1", "word": "Hello"},
      {"id": "2", "word": "World"}
    ],
    "target_language": "Spanish"
  }'
```

**Tests:**
- Unitarios: `tests/unit/test_batch_translate_use_case.py`, `tests/unit/test_translate_message_use_case.py`, `tests/unit/test_translation_endpoint.py`
- Integración: `tests/integration/test_translation_api.py`

---

# 📚 4. Learning Content Generation

## **9. POST /api/v1/learning/scenario**

Genera un escenario conversacional completo (personajes, vocabulario, objetivos).

---

## **10. POST /api/v1/learning/scenario-from-file**

Genera un escenario leyendo el contenido de un archivo (PDF, TXT, etc.).



---

# 🎓 5. Curriculum Management

## **18. POST /api/v1/curriculum/create**

Genera un currículo completo (temas, objetivos, unidades).

---

_(El documento continúa en este formato para los endpoints restantes; si quieres lo completo, lo genero TODO en un único archivo.)_

---

# 📂 Estructura de Carpetas

```
src/
├── application/use_cases/
│   ├── audio/
│   ├── conversation/
│   ├── translation/
│   ├── learning/
│   ├── assessment/
│   ├── curriculum/
│   └── course/
├── interfaces/api/
│   ├── v1/
│   │   ├── audio_routes.py
│   │   ├── conversation_routes.py
│   │   ├── translation_routes.py
│   │   ├── learning_routes.py
│   │   ├── assessment_routes.py
│   │   ├── curriculum_routes.py
│   │   └── course_routes.py
│   └── dtos/
│       ├── audio_dtos.py
│       ├── conversation_dtos.py
│       ├── translation_dtos.py
│       ├── learning_dtos.py
│       ├── assessment_dtos.py
│       ├── curriculum_dtos.py
│       └── course_dtos.py
```

---

# 📌 Patrones de Implementación

- Uso obligatorio de `@inject`
- Todos los casos de uso registrados en `container.py`
- DTOs con `Pydantic BaseModel`
- Manejo de excepciones estándar (`AIProviderError`, etc.)
- Pruebas unitarias + integración
- Cleanup de archivos temporales con `BackgroundTask`
- Autenticación con `Depends(verify_token)`

---

¿Quieres que genere el **documento completo con los 24 endpoints**, dividido por secciones y con tabla de contenido?  
Puedo producirlo listo para producción.
