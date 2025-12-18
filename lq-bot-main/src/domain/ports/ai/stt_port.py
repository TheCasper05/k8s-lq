from abc import ABC, abstractmethod
from pathlib import Path

from src.domain.models.audio import TranscriptionResult


class STTPort(ABC):
    """Port para servicios de Speech-to-Text (voz a texto)."""

    @abstractmethod
    async def transcribe_audio(
        self,
        audio: bytes | Path,
        language: str | None = None,
        temperature: float = 0.0,
        **kwargs,
    ) -> TranscriptionResult:
        """
        Transcribe audio a texto.

        Args:
            audio: Datos de audio (bytes) o ruta al archivo
            language: Código de idioma esperado (None = auto-detect)
            temperature: Control de aleatoriedad en la transcripción
            **kwargs: Parámetros específicos del proveedor

        Returns:
            TranscriptionResult con texto transcrito y metadata

        Raises:
            AIProviderError: Si hay error en la transcripción
        """
        pass

    @abstractmethod
    async def translate_audio(
        self, audio: bytes | Path, target_language: str = "en", **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe y traduce audio a un idioma destino.

        Args:
            audio: Datos de audio (bytes) o ruta al archivo
            target_language: Idioma destino para la traducción
            **kwargs: Parámetros específicos del proveedor

        Returns:
            TranscriptionResult con texto traducido y metadata
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Retorna lista de formatos de audio soportados"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass
