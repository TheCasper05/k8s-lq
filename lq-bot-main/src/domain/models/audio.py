from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class AudioOutput:
    """Salida de síntesis de voz (TTS)."""

    audio_data: bytes
    format: Literal["wav", "mp3", "ogg"]
    duration_seconds: float
    voice_used: str
    provider: str
    metadata: dict[str, Any]


@dataclass
class TranscriptionResult:
    """Resultado de transcripción de audio (STT)."""

    text: str
    language: str
    confidence: float | None
    provider: str
    duration_seconds: float
    metadata: dict[str, Any]


@dataclass
class VoiceConfig:
    """Configuración de una voz disponible."""

    id: str
    name: str
    language: str
    gender: Literal["male", "female", "neutral"]
    provider: str
