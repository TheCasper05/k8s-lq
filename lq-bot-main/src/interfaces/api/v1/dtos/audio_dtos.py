"""DTOs para endpoints de audio."""

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """Request para transcribir audio (cuando se envía como JSON)."""

    key: str | None = Field(
        None,
        description="Key del archivo en el storage (ej: audio/tts/audio_alloy_1.0_20251215_150647_bf352c87.mp3)",
    )
    url: str | None = Field(
        None,
        description="URL del archivo de audio (S3, HTTP, etc.) - Deprecated: usar 'key' en su lugar",
    )
    language: str | None = Field(None, description="Código de idioma esperado (None = auto-detect)")

    def get_key(self) -> str:
        """
        Obtiene la key del archivo, extrayéndola de la URL si es necesario.

        Returns:
            Key del archivo en el storage

        Raises:
            ValueError: Si no se proporciona ni key ni url
        """
        if self.key:
            return self.key

        if self.url:
            # Si es una URL de S3/DigitalOcean Spaces, extraer la key del path
            from urllib.parse import urlparse

            parsed = urlparse(self.url)
            if parsed.scheme in ("s3", "https") and (
                ".s3." in self.url or "digitaloceanspaces.com" in self.url
            ):
                return parsed.path.lstrip("/")
            # Si es una URL HTTP normal, devolver la URL completa para descargar
            return self.url

        raise ValueError("Debe proporcionarse 'key' o 'url'")


class TranscriptionResponse(BaseModel):
    """Response para transcripción de audio."""

    transcription: str = Field(..., description="Texto transcrito del audio")
    provider: str = Field(..., description="Proveedor de STT usado")
    model: str = Field(..., description="Modelo usado para la transcripción")


class CreateVoiceRequest(BaseModel):
    """Request para generar audio desde texto (TTS)."""

    text: str = Field(..., description="Texto a convertir en audio", min_length=1, max_length=5000)
    voice: str = Field(
        default="default",
        description="ID de la voz a usar (default usa la voz por defecto del proveedor)",
    )
    # language: str = Field(
    #     default="en", description="Código de idioma del texto (ISO 639-1, ej: 'en', 'es', 'fr')"
    # )
    audio_format: str = Field(
        default="mp3",
        description="Formato de audio deseado (mp3, ogg, wav)",
        pattern="^(mp3|ogg|wav)$",
    )
    speed: float = Field(
        default=1.0, description="Velocidad de reproducción (0.25 a 4.0)", ge=0.25, le=4.0
    )
    activity_type: str | None = Field(
        None,
        description="Tipo de actividad: 'conversations', 'listening', 'speaking' (opcional)",
        pattern="^(conversations|listening|speaking)$",
    )
    activity_id: str | None = Field(
        None,
        description="ID de la actividad (conversation_id, listening_id, speaking_id, etc.)",
    )


class CreateVoiceResponse(BaseModel):
    """Response para generación de audio (TTS)."""

    url: str = Field(..., description="URL pública del archivo de audio generado")
    key: str = Field(..., description="Key del archivo en el storage")
    duration_seconds: float = Field(..., description="Duración del audio en segundos")
    voice_used: str = Field(..., description="Voz usada para la síntesis")
    provider: str = Field(..., description="Proveedor de TTS usado")
    format: str = Field(..., description="Formato del archivo de audio")
    filename: str = Field(..., description="Nombre del archivo")
