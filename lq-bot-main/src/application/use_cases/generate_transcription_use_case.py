from pathlib import Path
from typing import Any

from src.domain.models.audio import TranscriptionResult
from src.domain.ports.ai.stt_port import STTPort


class GenerateTranscriptionUseCase:
    """Caso de uso para generar transcripciones a partir de audio."""

    def __init__(self, stt: STTPort):
        self.stt = stt

    async def execute(
        self,
        audio: bytes | Path,
        *,
        language: str | None = None,
        temperature: float = 0.0,
        translate: bool = False,
        target_language: str | None = None,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """
        Transcribe o traduce el audio según el modo solicitado.

        Args:
            audio: Bytes o Path del audio a procesar.
            language: Idioma objetivo para la transcripción.
            temperature: Parámetro de aleatoriedad.
            translate: Fuerza la traducción.
            target_language: Idioma destino cuando se traduce.
            **kwargs: Parámetros adicionales para el adaptador.
        """
        if translate:
            if not target_language:
                raise ValueError("Cuando se solicita traducción debe enviarse target_language.")
            return await self.stt.translate_audio(
                audio=audio,
                target_language=target_language,
                temperature=temperature,
                **kwargs,
            )

        return await self.stt.transcribe_audio(
            audio=audio,
            language=language,
            temperature=temperature,
            **kwargs,
        )
