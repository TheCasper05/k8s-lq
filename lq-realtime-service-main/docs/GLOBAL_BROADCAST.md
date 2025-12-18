# Sistema de Broadcast Global

El sistema de broadcast global permite enviar mensajes a **todos los usuarios conectados** en la plataforma, independientemente del tenant al que pertenezcan. Esta funcionalidad está diseñada para ser usada exclusivamente por el **panel de administración** del sistema.

## Características

- ✅ **Alcance global**: Envía mensajes a todos los usuarios conectados en todos los tenants
- ✅ **Seguridad**: Requiere autenticación con API key del sistema
- ✅ **Escalable**: Usa Redis Pub/Sub para distribuir mensajes a múltiples instancias del servidor
- ✅ **Tipos de mensaje**: Soporta diferentes tipos de mensajes (system, notification, etc.)
- ✅ **Sin límite de instancias**: Funciona correctamente con múltiples réplicas del servicio

## Seguridad

⚠️ **IMPORTANTE**: Este endpoint está protegido con una API key del sistema que debe mantenerse **secreta**. Solo el panel de administración del sistema debe tener acceso a esta API key.

### Configuración de la API Key

La API key del sistema se configura mediante la variable de entorno:

```bash
SYSTEM_API_KEY=tu-api-key-super-secreta-min-32-chars
```

**En producción**, asegúrate de:
1. Generar una API key fuerte y aleatoria (mínimo 32 caracteres)
2. Almacenarla de forma segura (variables de entorno, secrets manager, etc.)
3. No compartirla en repositorios de código
4. Rotarla periódicamente
5. Usar HTTPS para todas las comunicaciones

## Endpoint

### POST `/api/broadcast/global`

Envía un mensaje de broadcast global a todos los usuarios conectados.

#### Headers Requeridos

```
Content-Type: application/json
X-API-Key: {tu-system-api-key}
```

#### Request Body

```json
{
  "message_type": "system",
  "payload": {
    "title": "Título del mensaje",
    "message": "Contenido del mensaje",
    "priority": "high",
    "custom_field": "valor personalizado"
  },
  "from_user": "system"
}
```

**Campos:**
- `message_type` (string): Tipo de mensaje WebSocket. Valores: `system`, `notification`, `broadcast`, etc.
- `payload` (object): Contenido personalizado del mensaje. Puedes incluir cualquier campo necesario.
- `from_user` (string, opcional): Identificador del remitente. Por defecto: `"system"`

#### Response

**Success (200 OK):**
```json
{
  "success": true,
  "message": "Global broadcast sent successfully",
  "subscribers_reached": 3,
  "timestamp": "2025-12-09T13:44:22.621518"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid system API key"
}
```

**Error (500 Internal Server Error):**
```json
{
  "detail": "Failed to send broadcast: {error details}"
}
```

## Ejemplos de Uso

### Usando curl

```bash
curl -X POST http://localhost:8082/api/broadcast/global \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me-system-api-key-min-32-chars" \
  -d '{
    "message_type": "system",
    "payload": {
      "title": "Mantenimiento Programado",
      "message": "El sistema estará en mantenimiento el día 15 de diciembre de 2-4 AM",
      "priority": "high",
      "scheduled_time": "2025-12-15T02:00:00Z"
    }
  }'
```

### Usando Python

```python
import httpx

def send_global_announcement(api_key: str, title: str, message: str):
    url = "http://localhost:8082/api/broadcast/global"

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

    payload = {
        "message_type": "system",
        "payload": {
            "title": title,
            "message": message,
            "priority": "high",
        },
    }

    response = httpx.post(url, json=payload, headers=headers)
    return response.json()

# Uso
result = send_global_announcement(
    api_key="your-system-api-key",
    title="Actualización Importante",
    message="Nueva versión disponible"
)

print(f"Usuarios alcanzados: {result['subscribers_reached']}")
```

### Usando JavaScript/TypeScript

```typescript
async function sendGlobalBroadcast(
  apiKey: string,
  title: string,
  message: string
) {
  const response = await fetch('http://localhost:8082/api/broadcast/global', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify({
      message_type: 'system',
      payload: {
        title,
        message,
        priority: 'high',
      },
    }),
  });

  return await response.json();
}

// Uso
const result = await sendGlobalBroadcast(
  process.env.SYSTEM_API_KEY!,
  'Anuncio Importante',
  'Nuevas funcionalidades disponibles'
);

console.log(`Usuarios alcanzados: ${result.subscribers_reached}`);
```

## Casos de Uso

### 1. Anuncios de Mantenimiento

```json
{
  "message_type": "system",
  "payload": {
    "title": "Mantenimiento Programado",
    "message": "El sistema estará en mantenimiento de 2:00 AM a 4:00 AM",
    "priority": "high",
    "scheduled_time": "2025-12-15T02:00:00Z",
    "estimated_duration": "2 hours"
  }
}
```

### 2. Actualizaciones de Sistema

```json
{
  "message_type": "notification",
  "payload": {
    "title": "Nueva Versión Disponible",
    "message": "Actualiza tu aplicación para obtener las últimas funcionalidades",
    "version": "2.0.0",
    "priority": "normal",
    "action": {
      "type": "update",
      "url": "/download/latest"
    }
  }
}
```

### 3. Alertas de Seguridad

```json
{
  "message_type": "system",
  "payload": {
    "title": "Alerta de Seguridad",
    "message": "Por favor, actualiza tu contraseña inmediatamente",
    "priority": "urgent",
    "type": "security_alert",
    "action_required": true
  }
}
```

### 4. Avisos Generales

```json
{
  "message_type": "notification",
  "payload": {
    "title": "Nuevas Funcionalidades",
    "message": "Descubre las nuevas herramientas de aprendizaje",
    "priority": "low",
    "link": "/features/new",
    "dismissible": true
  }
}
```

## Arquitectura

### Flujo de Mensajes

```
┌─────────────────┐
│  Admin Panel    │
│  (Frontend)     │
└────────┬────────┘
         │ HTTP POST /api/broadcast/global
         │ Headers: X-API-Key
         ▼
┌─────────────────┐
│  API Endpoint   │ ◄── Verifica API Key
│  (FastAPI)      │
└────────┬────────┘
         │ Publica a Redis
         │ Canal: "global:broadcast"
         ▼
┌─────────────────┐
│  Redis Pub/Sub  │
└────────┬────────┘
         │ Distribuye a todas las instancias
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Instance │ │Instance │ │Instance │ │Instance │
   │    1    │ │    2    │ │    3    │ │    N    │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │           │
        ▼           ▼           ▼           ▼
   [Usuarios]  [Usuarios]  [Usuarios]  [Usuarios]
```

### Canales Redis

El sistema usa dos tipos de canales Redis:

1. **Canales de Tenant** (`tenant:{tenant_id}`): Para mensajes dentro de un tenant específico
2. **Canal Global** (`global:broadcast`): Para mensajes a todos los usuarios

Cada instancia del servidor WebSocket:
- Se suscribe automáticamente al canal global cuando se conecta el primer usuario
- Permanece suscrita mientras haya al menos una conexión activa
- Distribuye los mensajes globales a todas sus conexiones locales

## Monitoreo

### Verificar Conexiones Activas

```bash
curl http://localhost:8082/health
```

Respuesta:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-12-09T13:44:22.621518",
  "redis_connected": true,
  "active_connections": 150
}
```

### Ver Métricas Detalladas

```bash
curl http://localhost:8082/metrics
```

## Mejores Prácticas

### 1. Limitar Frecuencia

Evita enviar broadcasts masivos con demasiada frecuencia. Implementa rate limiting en tu panel de administración.

### 2. Priorizar Mensajes

Usa el campo `priority` para indicar la importancia:
- `urgent`: Alertas críticas de seguridad o sistema
- `high`: Mantenimientos programados, actualizaciones importantes
- `normal`: Anuncios generales
- `low`: Noticias, tips, nuevas funcionalidades

### 3. Mensajes Accionables

Cuando sea apropiado, incluye acciones claras:

```json
{
  "payload": {
    "title": "Actualización Requerida",
    "message": "Actualiza tu aplicación ahora",
    "action": {
      "type": "button",
      "label": "Actualizar Ahora",
      "url": "/update"
    }
  }
}
```

### 4. Internacionalización

Para mensajes multilingües, considera enviar identificadores de mensaje:

```json
{
  "payload": {
    "message_id": "maintenance.scheduled",
    "params": {
      "date": "2025-12-15",
      "time": "02:00",
      "duration": "2h"
    }
  }
}
```

### 5. Testing

Prueba siempre en un entorno de desarrollo antes de enviar broadcasts a producción:

```bash
# Desarrollo
curl -X POST http://localhost:8082/api/broadcast/global ...

# Staging
curl -X POST https://staging-api.example.com/api/broadcast/global ...

# Producción (con precaución)
curl -X POST https://api.example.com/api/broadcast/global ...
```

## Troubleshooting

### El broadcast no llega a los usuarios

1. **Verificar conexiones activas**: `curl http://localhost:8082/health`
2. **Verificar logs del servidor**: `docker compose logs ws-service -f`
3. **Verificar suscripciones Redis**: Buscar en logs "Subscribed to global broadcast channel"

### Error de autenticación

- Verifica que la API key en el header coincida con `SYSTEM_API_KEY` en el servidor
- Asegúrate de usar el header correcto: `X-API-Key`

### Subscribers reached = 0

- No hay conexiones WebSocket activas en ese momento
- El mensaje se publicó a Redis pero no hay instancias escuchando
- Verifica el estado del sistema con `/health` y `/metrics`

## Script de Prueba

Usa el script incluido para probar el sistema:

```bash
python3 docs/examples/test_global_broadcast.py \
  --api-key "your-system-api-key" \
  --title "Test Message" \
  --message "This is a test" \
  --priority "high"
```

## Seguridad y Compliance

- ✅ Autenticación con API key usando comparación de tiempo constante
- ✅ Solo accesible con credenciales del sistema
- ✅ Logs de auditoría para todos los broadcasts
- ✅ Rate limiting recomendado a nivel de aplicación
- ⚠️ Usa HTTPS en producción
- ⚠️ Almacena API keys de forma segura
- ⚠️ Implementa monitoreo de uso anómalo
