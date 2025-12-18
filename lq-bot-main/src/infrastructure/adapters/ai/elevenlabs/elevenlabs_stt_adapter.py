"""Adaptador STT para Eleven Labs Scribe v2 Realtime."""

from pathlib import Path
from typing import Any

import httpx

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.audio import TranscriptionResult
from src.domain.ports.ai.stt_port import STTPort


class ElevenLabsSTTAdapter(STTPort):
    """
    Implementación del port STT usando Eleven Labs Scribe v2 Realtime.

    Eleven Labs Scribe v2 es un modelo STT de última generación optimizado para
    transcripciones en tiempo real con alta precisión.

    API Doc: https://elevenlabs.io/docs/api-reference/scribe-v2
    """

    def __init__(
        self,
        api_key: str,
        model: str = "scribe-v2-realtime",
        language: str = "en",
    ):
        """
        Inicializa el adaptador de Eleven Labs STT.

        Args:
            api_key: API key de Eleven Labs
            model: Modelo STT a usar (scribe-v2-realtime por defecto)
            language: Idioma por defecto para transcripción
        """
        self.api_key = api_key
        self.model = model
        self.default_language = language
        self.provider_name = "elevenlabs"
        self.base_url = "https://api.elevenlabs.io/v1"

    async def transcribe_audio(
        self,
        audio: bytes | Path,
        language: str | None = None,
        temperature: float = 0.0,
        **kwargs,
    ) -> TranscriptionResult:
        """
        Transcribe audio a texto usando Eleven Labs Scribe v2.

        Args:
            audio: Datos de audio (bytes) o ruta al archivo
            language: Código de idioma (None = auto-detect)
            temperature: No usado en Eleven Labs, se mantiene por compatibilidad
            **kwargs: Parámetros adicionales

        Returns:
            TranscriptionResult con el texto transcrito

        Raises:
            AIProviderError: Si hay error en la transcripción
        """
        try:
            # Leer audio si es Path
            if isinstance(audio, Path):
                audio_data = audio.read_bytes()
            else:
                audio_data = audio

            # Preparar request
            url = f"{self.base_url}/audio-intelligence/speech-to-text"
            headers = {
                "xi-api-key": self.api_key,
            }

            # Eleven Labs acepta el audio como multipart/form-data
            files = {
                "audio": ("audio.mp3", audio_data, "audio/mpeg"),
            }

            # Parámetros opcionales
            data = {
                "model": self.model,
            }

            if language:
                data["language"] = language
            elif self.default_language:
                data["language"] = self.default_language

            # Hacer request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()

            result = response.json()

            # Eleven Labs retorna: {"text": "...", "language": "en", ...}
            return TranscriptionResult(
                text=result.get("text", ""),
                language=result.get("language", language or self.default_language),
                confidence=result.get("confidence"),  # Si está disponible
                provider=self.provider_name,
                duration_seconds=result.get("duration", 0.0),
                metadata={
                    "model": self.model,
                    "detected_language": result.get("detected_language"),
                },
            )

        except httpx.HTTPStatusError as e:
            raise AIProviderError(
                f"Error HTTP de Eleven Labs STT: {e.response.status_code} - {e.response.text}",
                provider=self.provider_name,
                original_error=e,
            ) from e
        except Exception as e:
            raise AIProviderError(
                f"Error en Eleven Labs STT: {e!s}", provider=self.provider_name, original_error=e
            ) from e

    async def translate_audio(
        self, audio: bytes | Path, target_language: str = "en", **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe y traduce audio.

        Nota: Eleven Labs Scribe v2 no soporta traducción directa,
        este método transcribe en el idioma original.
        Para traducción, usar el resultado con un LLM.

        Args:
            audio: Datos de audio
            target_language: Idioma destino (no usado)
            **kwargs: Parámetros adicionales

        Returns:
            TranscriptionResult con texto en idioma original
        """
        # Scribe v2 no soporta traducción directa, solo transcripción
        # Se podría combinar con un LLM para traducir después
        return await self.transcribe_audio(audio, language=None, **kwargs)

    def get_supported_formats(self) -> list[str]:
        """Retorna lista de formatos de audio soportados por Eleven Labs."""
        return [
            "mp3",
            "wav",
            "flac",
            "ogg",
            "m4a",
            "webm",
            "mp4",
            "mpeg",
            "mpga",
        ]

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        """Retorna información del modelo Scribe v2."""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": [
                "realtime_transcription",
                "multilingual",
                "high_accuracy",
                "auto_language_detection",
            ],
            "supported_formats": self.get_supported_formats(),
        }
