# 🔒 Estrategias de Seguridad para Archivos S3

Este documento explica cómo proteger los archivos almacenados en S3 y controlar el acceso a los mismos.

## 📋 Tabla de Contenidos

- [Resumen de Seguridad](#resumen-de-seguridad)
- [Configuración del Bucket S3](#configuración-del-bucket-s3)
- [URLs Prefirmadas](#urls-prefirmadas)
- [Validación de Permisos](#validación-de-permisos)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Flujo de Seguridad](#flujo-de-seguridad)
- [Implementar Validaciones Personalizadas](#implementar-validaciones-personalizadas)
- [Mejores Prácticas](#mejores-prácticas)

---

## Resumen de Seguridad

### ✅ Qué está implementado:

1. **Bucket S3 Privado**: Los archivos NO son públicos por defecto
2. **URLs Prefirmadas Temporales**: Acceso limitado en tiempo (1 hora por defecto)
3. **Autenticación Obligatoria**: Solo usuarios autenticados pueden obtener URLs
4. **Validación de Estructura**: Se valida que los paths sigan la estructura definida
5. **Sistema de Permisos**: Framework para validar acceso por contexto y recurso

### ⚠️ Qué debes implementar:

1. **Lógica de Permisos Específica**: Adaptar las validaciones en `permissions.py` a tu modelo de negocio
2. **Configuración del Bucket**: Asegurar que el bucket esté privado
3. **Logging y Auditoría**: Registrar accesos a archivos sensibles
4. **Rate Limiting**: Limitar requests por usuario/IP

---

## Configuración del Bucket S3

### Paso 1: Configurar Bucket como Privado

**En DigitalOcean Spaces:**

1. Ve a tu Space en el panel de control
2. Configura las siguientes políticas:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*",
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalType": "User"
        }
      }
    }
  ]
}
```

### Paso 2: Configurar CORS

Para permitir uploads desde el frontend:

```json
[
  {
    "AllowedOrigins": ["https://your-frontend-domain.com"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

**Para desarrollo local:**
```json
[
  {
    "AllowedOrigins": ["http://localhost:3000", "http://localhost:5173"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

---

## URLs Prefirmadas

### ¿Cómo funcionan?

Las URLs prefirmadas son URLs temporales firmadas con tu clave secreta de S3 que permiten acceso temporal a un archivo sin hacer público el bucket.

**Características:**
- ⏱️ **Temporales**: Expiran después de un tiempo definido (60-3600 segundos)
- 🔐 **Firmadas**: Contienen una firma criptográfica que S3 valida
- 🎯 **Específicas**: Solo dan acceso al archivo exacto solicitado
- 🚫 **No Reutilizables**: Después de expirar, dejan de funcionar

### Tipos de URLs Prefirmadas

#### 1. URLs de Upload (PUT)
Generadas por: `/api/v1/files/presigned-url`

Permiten **subir** un archivo a S3.

#### 2. URLs de Download (GET)
Generadas por: `/api/v1/files/presigned-download-url`

Permiten **descargar** un archivo de S3.

---

## Validación de Permisos

### Sistema de Permisos Implementado

El sistema valida permisos en **dos niveles**:

#### Nivel 1: Autenticación
```python
permission_classes = [IsAuthenticated]
```
Solo usuarios autenticados pueden hacer requests.

#### Nivel 2: Autorización por Contexto
```python
validate_file_access_permission(user, path_info)
validate_file_upload_permission(user, path_info)
```

Valida que el usuario tenga acceso al recurso específico según el contexto:
- **Activities**: Verificar participación en la actividad
- **Users**: Verificar ownership del archivo
- **Institutions**: Verificar membresía en la institución

### Archivo de Permisos

Las validaciones están en: [apps/files/permissions.py](permissions.py)

**Funciones principales:**
- `validate_file_access_permission()`: Valida acceso para descargas
- `validate_file_upload_permission()`: Valida acceso para uploads
- `_validate_activity_access()`: Lógica específica para activities
- `_validate_user_access()`: Lógica específica para users
- `_validate_institution_access()`: Lógica específica para institutions

---

## Endpoints Disponibles

### 1. Generar URL de Upload

**Endpoint:** `POST /api/v1/files/presigned-url`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "file_name": "recording.mp3",
  "file_category": "audio",
  "usage": "activities/conversations/{uuid}/messages/{uuid}.mp3",
  "file_size": 5242880,
  "metadata": {
    "Content-Type": "audio/mpeg",
    "x-amz-meta-user-id": "{user_uuid}",
    "x-amz-meta-sender-type": "user"
  }
}
```

**Response:**
```json
{
  "upload_url": "https://your-bucket.s3.amazonaws.com/...",
  "headers": {
    "Content-Length": "5242880",
    "Content-Type": "audio/mpeg",
    "x-amz-meta-user-id": "{user_uuid}",
    "x-amz-meta-sender-type": "user"
  },
  "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
  "expires_in": 3600
}
```

**Uso desde el frontend:**
```javascript
// 1. Obtener URL prefirmada
const response = await fetch('/api/v1/files/presigned-url', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    file_name: 'recording.mp3',
    file_category: 'audio',
    usage: `activities/conversations/${conversationId}/messages/${messageId}.mp3`,
    file_size: file.size,
    metadata: {
      'Content-Type': file.type,
      'x-amz-meta-user-id': userId,
      'x-amz-meta-sender-type': 'user'
    }
  })
});

const { upload_url, headers } = await response.json();

// 2. Subir archivo a S3
await fetch(upload_url, {
  method: 'PUT',
  headers: headers,
  body: file
});
```

### 2. Generar URL de Download

**Endpoint:** `POST /api/v1/files/presigned-download-url`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
  "force_download": false,
  "expiration": 3600
}
```

**Response:**
```json
{
  "download_url": "https://your-bucket.s3.amazonaws.com/...",
  "file_path": "activities/conversations/{uuid}/messages/{uuid}.mp3",
  "expires_in": 3600
}
```

**Uso desde el frontend:**
```javascript
// 1. Obtener URL de descarga
const response = await fetch('/api/v1/files/presigned-download-url', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    file_path: 'activities/conversations/123/messages/456.mp3',
    force_download: false,  // true para forzar descarga
    expiration: 1800  // 30 minutos
  })
});

const { download_url } = await response.json();

// 2. Usar la URL (en audio player, video player, etc.)
audioElement.src = download_url;

// O para descargar:
window.location.href = download_url;
```

---

## Flujo de Seguridad

### Flujo de Upload:

```
┌─────────────┐
│   Cliente   │
│  (Frontend) │
└──────┬──────┘
       │
       │ 1. POST /presigned-url
       │    + Auth Token
       │    + File metadata
       ▼
┌─────────────────────┐
│   Django Backend    │
│ ┌─────────────────┐ │
│ │ IsAuthenticated │ │ 2. Verifica autenticación
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Validate Path   │ │ 3. Valida estructura del path
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Check           │ │ 4. Verifica permisos del usuario
│ │ Permissions     │ │    (validate_file_upload_permission)
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Generate        │ │ 5. Genera URL prefirmada
│ │ Presigned URL   │ │
│ └─────────────────┘ │
└──────┬──────────────┘
       │
       │ 6. Retorna upload_url + headers
       ▼
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 7. PUT a upload_url
       │    + File binary
       ▼
┌─────────────┐
│     S3      │ 8. Valida firma y almacena
└─────────────┘
```

### Flujo de Download:

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 1. POST /presigned-download-url
       │    + Auth Token
       │    + file_path
       ▼
┌─────────────────────┐
│   Django Backend    │
│ ┌─────────────────┐ │
│ │ IsAuthenticated │ │ 2. Verifica autenticación
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Validate Path   │ │ 3. Valida estructura del path
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Check           │ │ 4. Verifica permisos del usuario
│ │ Permissions     │ │    (validate_file_access_permission)
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │ Generate        │ │ 5. Genera URL prefirmada
│ │ Download URL    │ │
│ └─────────────────┘ │
└──────┬──────────────┘
       │
       │ 6. Retorna download_url
       ▼
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 7. GET a download_url
       ▼
┌─────────────┐
│     S3      │ 8. Valida firma y sirve archivo
└─────────────┘
```

---

## Implementar Validaciones Personalizadas

### Ejemplo: Validar Acceso a Conversaciones

Edita `apps/files/permissions.py`:

```python
def _validate_activity_access(user, path_info: Dict[str, str]) -> bool:
    activity_type = path_info.get("activity_type")
    activity_id = path_info.get("activity_id")

    if activity_type == "conversations":
        from apps.conversations.models import Conversation

        # Buscar la conversación
        conversation = Conversation.objects.filter(id=activity_id).first()
        if not conversation:
            raise PermissionDenied("Conversación no encontrada")

        # Verificar que el usuario sea participante
        if not conversation.participants.filter(id=user.id).exists():
            raise PermissionDenied("No tienes acceso a esta conversación")

        return True

    # Otros activity types...
    return True
```

### Ejemplo: Validar Ownership de Archivos de Usuario

```python
def _validate_user_access(user, path_info: Dict[str, str]) -> bool:
    user_id = path_info.get("user_id")
    resource_type = path_info.get("resource_type")

    # Avatares son públicos
    if resource_type == "avatars":
        return True

    # Otros recursos requieren ser el dueño o admin
    if str(user.id) != user_id and not user.is_staff:
        raise PermissionDenied("No tienes acceso a este archivo")

    return True
```

### Ejemplo: Validar Membresía en Institución

```python
def _validate_institution_access(user, path_info: Dict[str, str]) -> bool:
    institution_id = path_info.get("institution_id")
    resource_type = path_info.get("resource_type")

    # Logos y banners son públicos
    if resource_type in ["logos", "banners"]:
        return True

    # Verificar membresía para otros recursos
    from apps.institutions.models import InstitutionMember

    is_member = InstitutionMember.objects.filter(
        institution_id=institution_id,
        user_id=user.id,
        is_active=True
    ).exists()

    if not is_member and not user.is_staff:
        raise PermissionDenied("No perteneces a esta institución")

    return True
```

---

## Mejores Prácticas

### 1. Configuración de Seguridad

✅ **Hacer:**
- Bucket S3 **siempre privado** en producción
- Usar HTTPS para todas las URLs
- Configurar CORS correctamente (solo dominios permitidos)
- Implementar rate limiting en los endpoints
- Validar permisos ANTES de generar URLs

❌ **Evitar:**
- Bucket público con archivos sensibles
- URLs prefirmadas con expiración muy larga (>1 hora)
- Generar URLs sin validar permisos
- Compartir URLs prefirmadas públicamente

### 2. Tiempo de Expiración

**Recomendaciones por uso:**
- **Audio/Video streaming**: 1800-3600 segundos (30-60 min)
- **Descargas de documentos**: 300-600 segundos (5-10 min)
- **Imágenes en UI**: 3600 segundos (1 hora)
- **Uploads**: 300-900 segundos (5-15 min)

### 3. Logging y Auditoría

Agrega logging para auditar accesos:

```python
import logging

logger = logging.getLogger(__name__)

def validate_file_access_permission(user, path_info: Dict[str, str]) -> bool:
    # ... validaciones

    # Log de acceso
    logger.info(
        f"File access granted",
        extra={
            'user_id': user.id,
            'file_path': path_info.get('file_path'),
            'context': path_info.get('context'),
            'timestamp': timezone.now()
        }
    )

    return True
```

### 4. Rate Limiting

Instala Django REST Framework throttling:

```python
# En views.py
from rest_framework.throttling import UserRateThrottle

class PresignedDownloadURLView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]  # Limitar requests por usuario

    # ... resto del código
```

Configura en `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour',  # 100 requests por hora por usuario
    }
}
```

### 5. Monitoreo

Monitorea:
- **Número de URLs generadas** por usuario/día
- **Archivos más accedidos**
- **Intentos de acceso no autorizados** (403 errors)
- **Tamaño de archivos subidos** por usuario

### 6. Seguridad Adicional

Para máxima seguridad, considera:

1. **CloudFront con Signed URLs**: Para CDN con control de acceso
2. **Encryption at Rest**: Encriptar archivos en S3 (Server-Side Encryption)
3. **Encryption in Transit**: Siempre usar HTTPS
4. **Bucket Versioning**: Habilitar versionado de archivos
5. **Object Lock**: Para archivos críticos que no deben ser eliminados

---

## Ejemplo de Flujo Completo

### Subir un Mensaje de Audio

```javascript
// Frontend
async function uploadAudioMessage(conversationId, audioBlob) {
  const messageId = uuidv4();
  const userId = getCurrentUserId();

  // 1. Solicitar URL de upload
  const response = await fetch('/api/v1/files/presigned-url', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      file_name: 'message.mp3',
      file_category: 'audio',
      usage: `activities/conversations/${conversationId}/messages/${messageId}.mp3`,
      file_size: audioBlob.size,
      metadata: {
        'Content-Type': 'audio/mpeg',
        'x-amz-meta-user-id': userId,
        'x-amz-meta-sender-type': 'user',
        'x-amz-meta-duration': '45'
      }
    })
  });

  if (!response.ok) {
    throw new Error('No tienes permiso para subir este archivo');
  }

  const { upload_url, headers, file_path } = await response.json();

  // 2. Subir a S3
  const uploadResponse = await fetch(upload_url, {
    method: 'PUT',
    headers: headers,
    body: audioBlob
  });

  if (!uploadResponse.ok) {
    throw new Error('Error al subir archivo');
  }

  // 3. Guardar referencia en tu DB
  await saveMessageToDatabase({
    id: messageId,
    conversation_id: conversationId,
    file_path: file_path,
    type: 'audio',
    user_id: userId
  });

  return file_path;
}
```

### Reproducir un Mensaje de Audio

```javascript
// Frontend
async function playAudioMessage(filePath) {
  // 1. Solicitar URL de descarga
  const response = await fetch('/api/v1/files/presigned-download-url', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      file_path: filePath,
      force_download: false,
      expiration: 1800  // 30 minutos
    })
  });

  if (!response.ok) {
    throw new Error('No tienes permiso para acceder a este archivo');
  }

  const { download_url } = await response.json();

  // 2. Reproducir audio
  const audio = new Audio(download_url);
  audio.play();
}
```

---

## Testing de Seguridad

### Test 1: Usuario no autenticado

```bash
curl -X POST http://localhost:8000/api/v1/files/presigned-download-url \
  -H "Content-Type: application/json" \
  -d '{"file_path": "users/123/documents/secret.pdf"}'

# Esperado: 401 Unauthorized
```

### Test 2: Usuario sin permisos

```bash
curl -X POST http://localhost:8000/api/v1/files/presigned-download-url \
  -H "Authorization: Bearer {token_usuario_a}" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "users/usuario-b-id/documents/private.pdf"}'

# Esperado: 403 Forbidden
```

### Test 3: Path traversal attack

```bash
curl -X POST http://localhost:8000/api/v1/files/presigned-download-url \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "users/../../../etc/passwd"}'

# Esperado: 400 Bad Request (validación de path)
```

---

## Recursos Adicionales

- **Código**: [apps/files/](.)
- **Configuración**: [apps/files/config.py](config.py)
- **Permisos**: [apps/files/permissions.py](permissions.py)
- **Resource Types**: [RESOURCE_TYPES.md](RESOURCE_TYPES.md)

---

**Última actualización:** 2025-12-13
