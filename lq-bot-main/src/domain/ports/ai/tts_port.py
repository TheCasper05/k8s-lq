from abc import ABC, abstractmethod
from typing import Literal

from src.domain.models.audio import AudioOutput, VoiceConfig


class TTSPort(ABC):
    """Port para servicios de Text-to-Speech (texto a voz)."""

    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
        audio_format: Literal["wav", "mp3", "ogg"] = "wav",
        speed: float = 1.0,
        **kwargs,
    ) -> AudioOutput:
        """
        Convierte texto a audio (voz).

        Args:
            text: Texto a sintetizar
            voice: ID de la voz a usar
            language: Código de idioma (en, es, fr, etc.)
            audio_format: Formato de salida del audio
            speed: Velocidad de reproducción (0.5 - 2.0)
            **kwargs: Parámetros específicos del proveedor

        Returns:
            AudioOutput con los datos de audio y metadata

        Raises:
            AIProviderError: Si hay error en la síntesis
        """
        pass

    @abstractmethod
    async def get_available_voices(self, language: str | None = None) -> list[VoiceConfig]:
        """
        Obtiene lista de voces disponibles.

        Args:
            language: Filtrar por idioma específico

        Returns:
            Lista de configuraciones de voz disponibles
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass
