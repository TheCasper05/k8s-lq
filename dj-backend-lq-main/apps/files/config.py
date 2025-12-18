"""
Configuraciones específicas de la app files.

Este módulo contiene todas las configuraciones relacionadas con la gestión
de archivos, incluyendo límites de tamaño por categoría y estructuras de paths.
"""

# File upload size limits (in bytes)
FILE_UPLOAD_MAX_SIZES = {
    "audio": 10 * 1024 * 1024,  # 10MB
    "image": 10 * 1024 * 1024,  # 10MB
    "pdf": 50 * 1024 * 1024,  # 50MB
    "video": 100 * 1024 * 1024,  # 100MB
}

FILE_UPLOAD_MAX_SIZE_GLOBAL = 100 * 1024 * 1024  # 100MB

# Path structure configuration for S3 bucket
# Formato: {context}/{context_id}/{resource_type}/{resource_id}.{ext}

# Contextos permitidos (nivel 1 del path)
ALLOWED_CONTEXTS = ["activities", "institutions", "users"]

# Activity types permitidos (nivel 2 para activities)
ACTIVITY_TYPES = ["conversations", "reading", "listening", "speaking", "writing"]

# Resource types por contexto
RESOURCE_TYPES = {
    "activities": {
        "conversations": ["messages", "transcripts", "attachments"],
        "reading": ["documents", "images"],
        "listening": ["audios", "transcripts"],
        "speaking": ["recordings"],
        "writing": ["submissions", "images"],
    },
    "institutions": ["logos", "banners", "documents", "media"],
    "users": ["avatars", "documents", "recordings", "attachments"],
}

# Mapeo de categorías a extensiones permitidas
CATEGORY_EXTENSIONS = {
    "audio": [".mp3", ".wav", ".ogg", ".m4a", ".aac"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "pdf": [".pdf"],
    "video": [".mp4", ".webm", ".mov", ".avi"],
}

# Categorías permitidas
ALLOWED_CATEGORIES = list(CATEGORY_EXTENSIONS.keys())

# Metadata keys permitidas (opcional)
ALLOWED_METADATA_KEYS = [
    "Content-Type",
    "x-amz-meta-user-id",
    "x-amz-meta-activity-id",
    "x-amz-meta-institution-id",
    "x-amz-meta-original-name",
    "x-amz-meta-description",
    "x-amz-meta-language",
    "x-amz-meta-duration",  # Para audio/video
    "x-amz-meta-sender-type",  # assistant, user, system
]
