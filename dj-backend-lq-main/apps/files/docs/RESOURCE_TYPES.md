# 📁 Estructura de Resource Types - S3 Bucket

Este documento describe la estructura de organización de archivos en el bucket S3 de LingoQuesto y cómo extenderla para agregar nuevos contextos y tipos de recursos.

## 📋 Tabla de Contenidos

- [Estructura General](#estructura-general)
- [Contextos y Resource Types](#contextos-y-resource-types)
  - [Activities](#1-activities)
  - [Institutions](#2-institutions)
  - [Users](#3-users)
- [Metadata Opcional](#metadata-opcional)
- [Cómo Agregar Nuevos Resource Types](#cómo-agregar-nuevos-resource-types)
- [Ejemplos de Uso](#ejemplos-de-uso)

---

## Estructura General

Todos los archivos en el bucket S3 siguen esta jerarquía:

```
{context}/{context_id}/{resource_type}/{resource_id}.{ext}
```

Donde:
- **context**: Categoría principal (`activities`, `institutions`, `users`)
- **context_id**: ID del recurso padre (UUID para activities, institutions, users)
- **resource_type**: Tipo de recurso específico del contexto
- **resource_id**: ID único del archivo (generalmente UUID)
- **ext**: Extensión del archivo

---

## Contextos y Resource Types

### 1. Activities

Archivos relacionados con actividades de aprendizaje.

**Estructura:**
```
activities/{activity_type}/{activity_id}/{resource_type}/{resource_id}.{ext}
```

#### Activity Types y sus Resource Types:

#### 1.1 Conversations
```
activities/conversations/{conversation_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `messages` | Archivos de mensajes (audio, texto, imágenes) | `messages/uuid.mp3`, `messages/uuid.png` |
| `transcripts` | Transcripciones de conversaciones | `transcripts/uuid.pdf` |
| `attachments` | Archivos adjuntos generales | `attachments/uuid.pdf` |

**Ejemplos:**
```
activities/conversations/123e4567-e89b-12d3-a456-426614174000/messages/abc123.mp3
activities/conversations/123e4567-e89b-12d3-a456-426614174000/transcripts/xyz789.pdf
```

#### 1.2 Reading
```
activities/reading/{reading_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `documents` | Documentos de lectura (PDFs, textos) | `documents/uuid.pdf` |
| `images` | Imágenes del contenido de lectura | `images/uuid.png` |

**Ejemplos:**
```
activities/reading/456e7890-e12b-34d5-a678-426614174001/documents/doc123.pdf
activities/reading/456e7890-e12b-34d5-a678-426614174001/images/img456.jpg
```

#### 1.3 Listening
```
activities/listening/{listening_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `audios` | Archivos de audio para ejercicios de listening | `audios/uuid.mp3` |
| `transcripts` | Transcripciones de los audios | `transcripts/uuid.pdf` |

**Ejemplos:**
```
activities/listening/789a0123-e45b-67d8-a901-426614174002/audios/audio123.mp3
activities/listening/789a0123-e45b-67d8-a901-426614174002/transcripts/trans456.pdf
```

#### 1.4 Speaking
```
activities/speaking/{speaking_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `recordings` | Grabaciones del usuario | `recordings/uuid.mp3` |

**Ejemplos:**
```
activities/speaking/012b3456-e78c-90d1-a234-426614174003/recordings/rec123.mp3
```

#### 1.5 Writing
```
activities/writing/{writing_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `submissions` | Ejercicios de escritura enviados | `submissions/uuid.pdf` |
| `images` | Imágenes de escritura (handwriting, screenshots) | `images/uuid.jpg` |

**Ejemplos:**
```
activities/writing/345c6789-e01d-23e4-a567-426614174004/submissions/sub123.pdf
activities/writing/345c6789-e01d-23e4-a567-426614174004/images/img789.png
```

---

### 2. Institutions

Archivos relacionados con instituciones educativas.

**Estructura:**
```
institutions/{institution_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `logos` | Logotipos de la institución | `logos/uuid.png` |
| `banners` | Imágenes de banner/portada | `banners/uuid.jpg` |
| `documents` | Documentos oficiales | `documents/uuid.pdf` |
| `media` | Otros medios (videos, imágenes generales) | `media/uuid.mp4` |

**Ejemplos:**
```
institutions/678d9012-e34e-56f7-a890-426614174005/logos/logo-main.png
institutions/678d9012-e34e-56f7-a890-426614174005/banners/banner-2024.jpg
institutions/678d9012-e34e-56f7-a890-426614174005/documents/regulations.pdf
```

---

### 3. Users

Archivos relacionados con usuarios.

**Estructura:**
```
users/{user_id}/{resource_type}/{resource_id}.{ext}
```

| Resource Type | Descripción | Ejemplos de Uso |
|--------------|-------------|-----------------|
| `avatars` | Fotos de perfil | `avatars/uuid.jpg` |
| `documents` | Documentos personales del usuario | `documents/uuid.pdf` |
| `recordings` | Grabaciones generales del usuario | `recordings/uuid.mp3` |
| `attachments` | Archivos adjuntos generales | `attachments/uuid.pdf` |

**Ejemplos:**
```
users/901e2345-e67f-89a0-b123-426614174006/avatars/avatar-2024.jpg
users/901e2345-e67f-89a0-b123-426614174006/documents/certificate.pdf
users/901e2345-e67f-89a0-b123-426614174006/recordings/practice-001.mp3
```

---

## Metadata Opcional

Puedes agregar metadata personalizada a los archivos usando headers S3. Las metadata keys permitidas están definidas en `apps/files/config.py`:

### Metadata Keys Soportadas:

| Key | Descripción | Ejemplo |
|-----|-------------|---------|
| `Content-Type` | Tipo MIME del archivo | `audio/mpeg`, `image/png` |
| `x-amz-meta-user-id` | ID del usuario que subió el archivo | `123e4567-e89b-12d3-a456-426614174000` |
| `x-amz-meta-activity-id` | ID de la actividad relacionada | `456e7890-e12b-34d5-a678-426614174001` |
| `x-amz-meta-institution-id` | ID de la institución relacionada | `789a0123-e45b-67d8-a901-426614174002` |
| `x-amz-meta-original-name` | Nombre original del archivo | `my-recording.mp3` |
| `x-amz-meta-description` | Descripción del archivo | `Practice conversation for lesson 5` |
| `x-amz-meta-language` | Idioma del contenido | `en`, `es`, `fr` |
| `x-amz-meta-duration` | Duración (para audio/video) | `180` (segundos) |
| `x-amz-meta-sender-type` | Tipo de emisor | `assistant`, `user`, `system` |

### Ejemplo con Metadata:

```json
{
  "file_name": "recording.mp3",
  "file_category": "audio",
  "usage": "activities/conversations/123e4567-e89b-12d3-a456-426614174000/messages/abc123.mp3",
  "file_size": 5242880,
  "metadata": {
    "Content-Type": "audio/mpeg",
    "x-amz-meta-user-id": "901e2345-e67f-89a0-b123-426614174006",
    "x-amz-meta-sender-type": "user",
    "x-amz-meta-language": "en",
    "x-amz-meta-duration": "120"
  }
}
```

---

## Cómo Agregar Nuevos Resource Types

### Paso 1: Editar `apps/files/config.py`

#### Agregar un nuevo Activity Type:

```python
# En ACTIVITY_TYPES
ACTIVITY_TYPES = [
    "conversations",
    "reading",
    "listening",
    "speaking",
    "writing",
    "vocabulary",  # ← Nuevo activity type
]

# En RESOURCE_TYPES
RESOURCE_TYPES = {
    "activities": {
        # ... existing types
        "vocabulary": ["flashcards", "exercises", "images"],  # ← Nuevos resource types
    },
    # ...
}
```

#### Agregar un nuevo Resource Type a un contexto existente:

```python
RESOURCE_TYPES = {
    "activities": {
        "conversations": [
            "messages",
            "transcripts",
            "attachments",
            "feedback",  # ← Nuevo resource type
        ],
        # ...
    },
    "institutions": [
        "logos",
        "banners",
        "documents",
        "media",
        "certificates",  # ← Nuevo resource type
    ],
    "users": [
        "avatars",
        "documents",
        "recordings",
        "attachments",
        "certificates",  # ← Nuevo resource type
    ],
}
```

#### Agregar un nuevo Contexto completo:

```python
# Agregar a ALLOWED_CONTEXTS
ALLOWED_CONTEXTS = ["activities", "institutions", "users", "courses"]  # ← Nuevo contexto

# Agregar resource types para el nuevo contexto
RESOURCE_TYPES = {
    # ... existing contexts
    "courses": ["materials", "videos", "documents", "assessments"],  # ← Nuevo contexto
}
```

### Paso 2: Actualizar `apps/files/validators.py`

Si agregaste un **nuevo contexto**, necesitas crear una función de validación:

```python
def validate_path_structure(usage: str) -> dict:
    # ... existing code

    # Agregar el nuevo contexto
    elif context == "courses":
        return _validate_courses_path(parts)


def _validate_courses_path(parts: list) -> dict:
    """
    Valida path para courses.
    Formato: courses/{course_id}/{resource_type}/{resource_id}.{ext}
    """
    if len(parts) < 4:
        raise ValidationError(
            "Path de courses debe tener formato: "
            "courses/{course_id}/{resource_type}/{resource_id}.{ext}"
        )

    context, course_id, resource_type, *file_parts = parts

    # Validar resource_type
    allowed_resource_types = RESOURCE_TYPES["courses"]
    if resource_type not in allowed_resource_types:
        raise ValidationError(
            f"Resource type '{resource_type}' no permitido para courses. "
            f"Tipos permitidos: {', '.join(allowed_resource_types)}"
        )

    # Validar formato de ID (UUID)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(course_id):
        raise ValidationError(
            f"Course ID '{course_id}' debe ser un UUID válido"
        )

    return {
        "context": context,
        "course_id": course_id,
        "resource_type": resource_type,
        "file_path": "/".join(file_parts) if file_parts else None,
    }
```

### Paso 3: Agregar Nuevas Metadata Keys (Opcional)

Si necesitas metadata adicional:

```python
# En apps/files/config.py
ALLOWED_METADATA_KEYS = [
    # ... existing keys
    "x-amz-meta-difficulty-level",  # ← Nueva metadata key
    "x-amz-meta-topic",
]
```

---

## Ejemplos de Uso

### Ejemplo 1: Subir un mensaje de audio en una conversación

**Request:**
```json
POST /api/files/presigned-url/

{
  "file_name": "message-123.mp3",
  "file_category": "audio",
  "usage": "activities/conversations/123e4567-e89b-12d3-a456-426614174000/messages/abc-def-123.mp3",
  "file_size": 2097152,
  "metadata": {
    "Content-Type": "audio/mpeg",
    "x-amz-meta-user-id": "901e2345-e67f-89a0-b123-426614174006",
    "x-amz-meta-sender-type": "user",
    "x-amz-meta-duration": "45"
  }
}
```

**Response:**
```json
{
  "upload_url": "https://your-bucket.s3.amazonaws.com/...",
  "headers": {
    "Content-Length": "2097152",
    "Content-Type": "audio/mpeg",
    "x-amz-meta-user-id": "901e2345-e67f-89a0-b123-426614174006",
    "x-amz-meta-sender-type": "user",
    "x-amz-meta-duration": "45"
  },
  "file_path": "activities/conversations/123e4567-e89b-12d3-a456-426614174000/messages/abc-def-123.mp3",
  "expires_in": 3600
}
```

### Ejemplo 2: Subir un logo de institución

**Request:**
```json
POST /api/files/presigned-url/

{
  "file_name": "logo.png",
  "file_category": "image",
  "usage": "institutions/678d9012-e34e-56f7-a890-426614174005/logos/main-logo.png",
  "file_size": 524288,
  "metadata": {
    "Content-Type": "image/png",
    "x-amz-meta-original-name": "MySchool_Logo_2024.png"
  }
}
```

### Ejemplo 3: Subir un documento de lectura

**Request:**
```json
POST /api/files/presigned-url/

{
  "file_name": "lesson-5.pdf",
  "file_category": "pdf",
  "usage": "activities/reading/456e7890-e12b-34d5-a678-426614174001/documents/lesson-5.pdf",
  "file_size": 1048576,
  "metadata": {
    "Content-Type": "application/pdf",
    "x-amz-meta-language": "es",
    "x-amz-meta-description": "Reading comprehension - Intermediate level"
  }
}
```

---

## Categorías de Archivos Soportadas

Las categorías definen el tipo de archivo y sus extensiones permitidas:

| Categoría | Extensiones Permitidas | Tamaño Máximo |
|-----------|----------------------|---------------|
| `audio` | `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac` | 10 MB |
| `image` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp` | 10 MB |
| `pdf` | `.pdf` | 50 MB |
| `video` | `.mp4`, `.webm`, `.mov`, `.avi` | 100 MB |

**Límite global:** 100 MB para cualquier archivo.

Para modificar estos límites, edita `FILE_UPLOAD_MAX_SIZES` en [apps/files/config.py](config.py).

---

## Validaciones de Seguridad

El sistema valida automáticamente:

✅ **Path traversal**: No permite `..` en paths
✅ **Caracteres peligrosos**: Bloquea caracteres como `;`, `$`, `|`, etc.
✅ **UUIDs válidos**: Los IDs deben ser UUIDs válidos
✅ **Estructura correcta**: Valida que el path siga el formato esperado
✅ **Resource types permitidos**: Solo acepta resource types configurados
✅ **Extensiones permitidas**: Valida extensión según categoría
✅ **Tamaños de archivo**: Valida límites por categoría y global
✅ **Metadata válida**: Solo acepta metadata keys permitidas

---

## Notas Importantes

1. **IDs deben ser UUIDs**: Todos los IDs (`activity_id`, `institution_id`, `user_id`, `resource_id`) deben ser UUIDs válidos en formato `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`.

2. **No validación de ownership**: El sistema NO valida automáticamente que el usuario tenga permisos sobre el recurso. Esto debe implementarse en la lógica de negocio del frontend o mediante middlewares.

3. **Metadata es opcional**: Puedes omitir el campo `metadata` completamente o enviar un objeto vacío `{}`.

4. **Content-Type**: Aunque es opcional, se recomienda siempre enviar `Content-Type` en la metadata para que S3 devuelva el tipo correcto al descargar el archivo.

5. **Expiración de URLs**: Por defecto, las URLs prefirmadas expiran en 1 hora (3600 segundos). Puedes ajustar esto en la configuración `DO_SPACES_PRESIGN_EXPIRE_SECONDS`.

---

## Recursos Adicionales

- **Configuración**: [apps/files/config.py](config.py)
- **Validadores**: [apps/files/validators.py](validators.py)
- **Servicio de URLs**: [apps/files/services.py](services.py)
- **API View**: [apps/files/views.py](views.py)

---

**Última actualización:** 2025-12-13
