from typing import Any, Literal

from src.domain.models.audio import AudioOutput
from src.domain.ports.ai.tts_port import TTSPort


class GenerateAudioResponseUseCase:
    """Caso de uso para generar respuestas habladas (TTS)."""

    def __init__(self, tts: TTSPort):
        self.tts = tts

    async def execute(
        self,
        text: str,
        *,
        voice: str = "default",
        # language: str = "en",
        audio_format: Literal["wav", "mp3", "ogg"] = "wav",
        speed: float = 1.0,
        **kwargs: Any,
    ) -> AudioOutput:
        """
        Genera audio utilizando el adaptador TTS configurado.

        Args:
            text: Texto a convertir en audio.
            voice: ID de la voz o "default".
            language: Idioma del texto.
            audio_format: Formato del audio resultante.
            speed: Velocidad de reproducción deseada.
            **kwargs: Parámetros adicionales para el adaptador.
        """
        return await self.tts.synthesize_speech(
            text=text,
            voice=voice,
            # language=language,
            audio_format=audio_format,
            speed=speed,
            **kwargs,
        )
