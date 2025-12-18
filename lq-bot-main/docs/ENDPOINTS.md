# 📡 Documentación de Endpoints API

Esta documentación describe todos los endpoints disponibles en la API de LingoQuesto Bot.

**Base URL:** `/api/v1` (excepto `/health`)

---

## 🏥 Health Check

### `GET /health`

Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200 OK` - API funcionando correctamente

---

## 💬 Chat Endpoints

### `POST /api/v1/chat/generate`

Genera una respuesta de texto usando LLM con configuración personalizada.

**Descripción:** Endpoint genérico para generar respuestas de texto con control total sobre el prompt del sistema, temperatura y tokens máximos.

**Request Body:**
```json
{
  "message": "Hola, ¿cómo estás?",
  "system_prompt": "Eres un asistente amigable y profesional.",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Campos:**
- `message` (string, requerido): Mensaje del usuario. Mínimo 1 carácter, máximo 10000 caracteres.
- `system_prompt` (string, opcional): Prompt del sistema con instrucciones. Máximo 5000 caracteres.
- `temperature` (float, opcional): Temperatura para la generación (0-2). Default: 0.7
- `max_tokens` (int, opcional): Máximo de tokens a generar (1-4000). Default: 1000

**Response:**
```json
{
  "content": "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte?",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 25,
  "finish_reason": "stop"
}
```

**Campos de Respuesta:**
- `content` (string): Contenido de la respuesta generada
- `provider` (string): Proveedor de IA usado (openai, grok, etc.)
- `model` (string): Modelo específico usado
- `tokens_used` (int): Total de tokens consumidos
- `finish_reason` (string): Razón de finalización (stop, length, etc.)

**Status Codes:**
- `200 OK` - Respuesta generada exitosamente
- `422 Unprocessable Entity` - Error de validación en el request
- `500 Internal Server Error` - Error al generar la respuesta

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8081/api/v1/chat/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explícame qué es Python",
    "system_prompt": "Eres un profesor de programación experto.",
    "temperature": 0.5,
    "max_tokens": 500
  }'
```

---

## 🗣️ Conversation Endpoints

### `POST /api/v1/conversation/text_answer`

Genera una respuesta de texto en el contexto de un escenario de conversación educativo.

**Descripción:** Endpoint especializado para conversaciones educativas con escenarios predefinidos (roleplay, teacher, knowledge). Utiliza prompts del sistema configurados según el tipo de escenario.

**Request Body:**
```json
{
  "message": "I'd like to order a pizza",
  "scenario_type": "roleplay",
  "response_id": "conv_123",
  "theme": "Restaurant conversation",
  "assistant_role": "waiter",
  "user_role": "customer",
  "potential_directions": "ordering food, asking about menu, paying the bill",
  "setting": "Italian restaurant",
  "example": "Customer: I'd like pizza. Waiter: What size?",
  "additional_data": "Use polite language and be friendly",
  "practice_topic": null,
  "language": "English"
}
```

**Campos:**
- `message` (string, requerido): Mensaje del usuario. Mínimo 1 carácter, máximo 10000 caracteres.
- `scenario_type` (string, requerido): Tipo de escenario. Valores válidos: `"roleplay"`, `"teacher"`, `"knowledge"`
- `response_id` (string, opcional): ID de la respuesta anterior para mantener historial de conversación
- `theme` (string, opcional): Tema de la conversación
- `language` (string, opcional): Idioma de la conversación (default: "English")
- `assistant_role` (string, opcional): Rol que juega el asistente en el escenario
- `user_role` (string, opcional): Rol que juega el usuario en el escenario
- `potential_directions` (string, opcional): Posibles direcciones o temas que puede tomar la conversación
- `setting` (string, opcional): Escenario físico o situacional donde ocurre la conversación
- `example` (string, opcional): Ejemplo de intercambio conversacional (una línea)
- `additional_data` (string, opcional): Datos adicionales importantes para la conversación
- `practice_topic` (string, opcional): Tema específico a practicar (usado principalmente en escenarios "teacher")

**Response:**
```json
{
  "content": "Welcome! 🌸 What size pizza would you like? We have small, medium, and large. 😊",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "tokens_used": 45,
  "finish_reason": "stop",
  "response_id": "resp_456",
  "metadata": {
    "completion_tokens": 20,
    "prompt_tokens": 25
  },
  "created_at": "2024-01-15T10:30:00"
}
```

**Campos de Respuesta:**
- `content` (string): Contenido de la respuesta generada
- `provider` (string): Proveedor de IA usado
- `model` (string): Modelo específico usado
- `tokens_used` (int): Total de tokens consumidos
- `finish_reason` (string): Razón de finalización
- `response_id` (string, opcional): ID de la respuesta (para continuar la conversación)
- `metadata` (object, opcional): Metadatos adicionales (tokens de entrada/salida)
- `created_at` (string): Timestamp de creación

**Tipos de Escenario:**

1. **`roleplay`**: Conversación de roleplay donde el estudiante practica en un escenario realista
   - Requiere: `theme`, `assistant_role`, `user_role`, `potential_directions`, `setting`, `example`, `additional_data`
   - Usa el prompt: `conversations/roleplay_v1.txt`

2. **`teacher`**: Conversación donde el AI actúa como profesor y corrige al estudiante
   - Requiere: `practice_topic`, `potential_directions`, `theme`, `additional_data`
   - Usa el prompt: `conversations/teacher_v1.txt`

3. **`knowledge`**: Conversación educativa sobre un tema específico
   - Requiere: `theme`, `practice_topic`, `additional_data`
   - Usa el prompt correspondiente según la implementación

**Status Codes:**
- `200 OK` - Respuesta generada exitosamente
- `422 Unprocessable Entity` - Error de validación en el request
- `500 Internal Server Error` - Error al generar la respuesta

**Ejemplo de uso - Roleplay:**
```bash
curl -X POST "http://localhost:8081/api/v1/conversation/text_answer" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I would like to make a reservation",
    "scenario_type": "roleplay",
    "theme": "Restaurant reservation",
    "assistant_role": "restaurant host",
    "user_role": "customer",
    "potential_directions": "checking availability, selecting time, party size",
    "setting": "Fine dining restaurant",
    "example": "Customer: I want a table. Host: For how many people?",
    "additional_data": "Be professional and helpful"
  }'
```

**Ejemplo de uso - Teacher:**
```bash
curl -X POST "http://localhost:8081/api/v1/conversation/text_answer" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to practice English",
    "scenario_type": "teacher",
    "practice_topic": "verb tenses",
    "potential_directions": "past simple, present perfect, future",
    "theme": "Grammar practice",
    "additional_data": "Focus on past simple tense"
  }'
```

**Ejemplo con historial de conversación:**
```bash
# Primera respuesta
curl -X POST "http://localhost:8081/api/v1/conversation/text_answer" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "scenario_type": "roleplay",
    "theme": "Restaurant",
    "assistant_role": "waiter",
    "user_role": "customer"
  }'

# Respuesta de seguimiento (usando response_id de la respuesta anterior)
curl -X POST "http://localhost:8081/api/v1/conversation/text_answer" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I would like a pizza",
    "scenario_type": "roleplay",
    "response_id": "resp_123",
    "theme": "Restaurant",
    "assistant_role": "waiter",
    "user_role": "customer"
  }'
```

---

### `POST /api/v1/conversation/suggestions`

Genera sugerencias de respuestas para ayudar al estudiante a continuar una conversación.

**Descripción:** Endpoint especializado para generar 3 sugerencias de respuestas que el estudiante puede usar para responder al mensaje del asistente en un contexto educativo. Las sugerencias están diseñadas para ser útiles, contextualmente relevantes y mantener la conversación fluida.

**Request Body:**
```json
{
  "assistant_message": "Hello! How can I help you today?",
  "scenario_context": "Going on a trip to Paris",
  "language": "English"
}
```

**Campos:**
- `assistant_message` (string, requerido): Mensaje del asistente al que el estudiante debe responder
- `scenario_context` (string, requerido): Contexto del escenario educativo donde ocurre la conversación
- `language` (string, requerido): Idioma en el que se deben generar las sugerencias (debe coincidir con el idioma del mensaje del asistente)

**Response:**
```json
{
  "suggestions": [
    "I'm doing great, thank you! How about you? 😊",
    "I'm fine, thanks for asking! What can you help me with?",
    "I'm well, thank you! I'm excited about my trip to Paris! ✈️"
  ],
  "model": "gpt-4o-mini",
  "tokens_used": 85
}
```

**Campos de Respuesta:**
- `suggestions` (array[string]): Array de exactamente 3 sugerencias de respuestas. Cada sugerencia tiene menos de 40 palabras y está en el idioma especificado
- `model` (string): Modelo de IA usado para generar las sugerencias
- `tokens_used` (int): Total de tokens consumidos en la generación

**Características:**
- Genera exactamente 3 sugerencias por request
- Las sugerencias están adaptadas al contexto del escenario
- Incluyen emojis para mantener el tono fresco y amigable
- Están en el idioma especificado en el request
- Son contextualmente relevantes al mensaje del asistente y al escenario

**Status Codes:**
- `200 OK` - Sugerencias generadas exitosamente
- `422 Unprocessable Entity` - Error de validación en el request (campos faltantes, valores inválidos)
- `500 Internal Server Error` - Error al generar las sugerencias

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8081/api/v1/conversation/suggestions" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_message": "Welcome to our restaurant! What would you like to order?",
    "scenario_context": "Restaurant conversation - ordering food",
    "language": "English"
  }'
```

**Ejemplo de uso en español:**
```bash
curl -X POST "http://localhost:8081/api/v1/conversation/suggestions" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_message": "¡Hola! ¿En qué puedo ayudarte hoy?",
    "scenario_context": "Conversación en un restaurante - pedir comida",
    "language": "Spanish"
  }'
```

**Notas importantes:**
- El `language` debe coincidir con el idioma del `assistant_message`. Si el mensaje está en español, el `language` debe ser "Spanish"
- Las sugerencias se generan usando un schema JSON estricto que garantiza exactamente 3 sugerencias
- El endpoint utiliza prompts especializados (`suggestions_system_v1` y `suggestions_user_v1`) optimizados para generar sugerencias educativas

---

## 🎭 Scenario Endpoints

### `POST /api/v1/scenario/create`

Genera un escenario de conversación completo basado en una solicitud del usuario.

**Descripción:** Endpoint para crear escenarios educativos de conversación. Puede usar un proceso multi-agente (si `LQBOT_SCENARIO_MULTI_AGENT=true`) o un solo llamado al LLM. El escenario generado incluye todos los campos necesarios para iniciar una conversación educativa.

**Request Body:**
```json
{
  "user_request": "I want to practice ordering tacos in Spanish with a friendly waiter at a traditional mercado in Mexico City",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Campos:**
- `user_request` (string, requerido): Solicitud del usuario para crear el escenario. Mínimo 1 carácter.
- `temperature` (float, opcional): Temperatura para la generación (0-2). Default: 0.7
- `max_tokens` (int, opcional): Máximo de tokens a generar (1-16000). Default: 2000

**Response:**
```json
{
  "scenario": {
    "title": "Ordering Tacos in Mexico City",
    "assistant_gender": "male",
    "scenario_type": "roleplay",
    "practice_topic": "food ordering",
    "complete_description": "You are a tourist ordering tacos at a traditional mercado in Mexico City. I am a friendly waiter who will help you practice your Spanish while ordering delicious tacos.",
    "theme": "Ordering Food at a Traditional Market",
    "assistant_role": "friendly waiter",
    "user_role": "tourist",
    "setting": "A traditional mercado in Mexico City with colorful stalls and the aroma of fresh food",
    "potential_directions": "Asking about ingredients, Ordering different dishes, Discussing prices, Learning food vocabulary, Cultural exchange",
    "example": "Assistant: ¡Bienvenido! ¿Qué le gustaría ordenar? User: Quisiera tres tacos, por favor.",
    "additional_data": [],
    "appropriate": true
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "tokens_used": 500,
    "finish_reason": "stop"
  }
}
```

**Campos de Respuesta - Scenario:**
- `title` (string): Título del escenario
- `assistant_gender` (string): Género del asistente ("male" o "female")
- `scenario_type` (string): Tipo de escenario ("teacher", "roleplay" o "knowledge")
- `practice_topic` (string): Tema específico a practicar
- `complete_description` (string): Descripción completa del escenario para el usuario
- `theme` (string): Tema resumido en una línea
- `assistant_role` (string): Rol que juega el asistente
- `user_role` (string): Rol que juega el usuario
- `setting` (string): Escenario físico o situacional
- `potential_directions` (string): Cinco direcciones posibles de la conversación (separadas por comas)
- `example` (string): Ejemplo de intercambio conversacional (una línea)
- `additional_data` (array[string]): Datos adicionales importantes
- `appropriate` (boolean): Indica si el tema es apropiado para todas las edades

**Campos de Respuesta - Metadata:**
- `provider` (string): Proveedor de IA usado
- `model` (string): Modelo específico usado
- `tokens_used` (int): Total de tokens consumidos
- `finish_reason` (string): Razón de finalización

**Modo Multi-Agent:**

Cuando `LQBOT_SCENARIO_MULTI_AGENT=true`, el endpoint utiliza un proceso multi-paso:

1. **Paso 1 - `prepare_context`**: Extrae `context` y `language` de la solicitud del usuario
2. **Paso 2 - `build_scenario`**: Genera el escenario completo usando el contexto preparado

Este modo permite una generación más estructurada y controlada del escenario.

**Modo Single LLM:**

Cuando `LQBOT_SCENARIO_MULTI_AGENT=false`, el endpoint hace un solo llamado al LLM con el prompt directo.

**Status Codes:**
- `200 OK` - Escenario generado exitosamente
- `400 Bad Request` - Error al parsear la respuesta JSON o error en el proceso multi-agent
- `422 Unprocessable Entity` - Error de validación en el request
- `500 Internal Server Error` - Error al generar el escenario

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8000/api/v1/scenario/create" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "user_request": "I want to practice ordering food in a French restaurant",
    "temperature": 0.5,
    "max_tokens": 3000
  }'
```

**Ejemplo de uso con parámetros mínimos:**
```bash
curl -X POST "http://localhost:8000/api/v1/scenario/create" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "user_request": "Create a scenario for practicing past tense in English"
  }'
```

**Variables de Entorno:**
- `LQBOT_SCENARIO_MULTI_AGENT` (boolean): Habilita/deshabilita el modo multi-agent. Default: `true`

**Notas importantes:**
- El endpoint requiere autenticación mediante header `X-API-Key`
- El `user_request` debe ser descriptivo para obtener mejores resultados
- El escenario generado puede usarse directamente con `/api/v1/conversation/text_answer`
- En modo multi-agent, los tokens usados se suman de todos los pasos del proceso

---

## 🔧 Configuración y Errores

### Manejo de Errores

Todos los endpoints devuelven errores en el siguiente formato:

```json
{
  "detail": "Mensaje de error descriptivo"
}
```

**Códigos de Error Comunes:**
- `400 Bad Request` - Request mal formado
- `422 Unprocessable Entity` - Error de validación (campos faltantes, valores inválidos)
- `500 Internal Server Error` - Error interno del servidor o del proveedor de IA

### Variables de Entorno

Los endpoints utilizan la configuración definida en las variables de entorno (ver `src/config.py`):

- `LQBOT_LLM_PROVIDER` - Proveedor LLM (openai, grok)
- `LQBOT_OPENAI_API_KEY` - API Key de OpenAI
- `LQBOT_OPENAI_LLM_MODEL` - Modelo de OpenAI (default: gpt-4o-mini)
- `LQBOT_SCENARIO_MULTI_AGENT` - Usar multi-agent manager para creación de escenarios (default: true)

---

## 📚 Referencias

- **Código de rutas:** `src/interfaces/api/v1/`
- **DTOs:** `src/interfaces/api/dtos/`
- **Servicios:** `src/domain/services/`
- **Casos de uso:** `src/application/use_cases/`
- **Configuración:** `src/config.py`

---

## 🧪 Testing

Los endpoints están cubiertos por tests de integración y unitarios:

- `tests/integration/test_chat_api.py` - Tests para `/api/v1/chat/generate`
- `tests/integration/test_text_answer_api.py` - Tests para `/api/v1/conversation/text_answer`
- `tests/unit/test_generate_conversation_suggestions_use_case.py` - Tests unitarios para el caso de uso de sugerencias
- `tests/unit/test_create_scenario_use_case.py` - Tests unitarios para el caso de uso de creación de escenarios

Para ejecutar los tests:
```bash
pytest tests/integration/
pytest tests/unit/test_create_scenario_use_case.py
```

