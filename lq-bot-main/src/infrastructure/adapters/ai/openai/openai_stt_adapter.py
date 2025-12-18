import io
from pathlib import Path
from typing import Any

from openai import AsyncOpenAI

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.audio import TranscriptionResult
from src.domain.ports.ai.stt_port import STTPort


class OpenAISTTAdapter(STTPort):
    """Implementación del port STT usando OpenAI Whisper / Speech APIs."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini-transcribe"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.provider_name = "openai"

    async def transcribe_audio(
        self,
        audio: bytes | Path,
        language: str | None = None,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """Transcribe audio usando OpenAI."""
        try:
            stream, estimated_duration = self._prepare_audio(audio)
            params: dict[str, Any] = {
                "model": self.model,
                "file": stream,
                "temperature": temperature,
            }

            if language:
                params["language"] = language

            params.update(kwargs)

            response = await self.client.audio.transcriptions.create(**params)
            return self._build_result(
                response=response,
                language=language,
                temperature=temperature,
                duration_hint=estimated_duration,
                translation_mode=False,
            )

        except Exception as exc:
            print(f"Error al transcribir audio con OpenAI: {exc}")
            raise AIProviderError(
                "Error al transcribir audio con OpenAI",
                provider=self.provider_name,
                original_error=exc,
            ) from exc

    async def translate_audio(
        self,
        audio: bytes | Path,
        target_language: str = "en",
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """Transcribe y traduce audio usando el endpoint de traducciones."""
        try:
            stream, estimated_duration = self._prepare_audio(audio)
            params: dict[str, Any] = {
                "model": self.model,
                "file": stream,
                "temperature": temperature,
                "language": target_language,
            }
            params.update(kwargs)

            translate_endpoint = getattr(self.client.audio, "translations", None)
            if translate_endpoint is None:
                return await self.transcribe_audio(
                    audio=audio, language=target_language, temperature=temperature, **kwargs
                )

            response = await translate_endpoint.create(**params)
            return self._build_result(
                response=response,
                language=target_language,
                temperature=params["temperature"],
                duration_hint=estimated_duration,
                translation_mode=True,
            )

        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(
                "Error al traducir audio con OpenAI",
                provider=self.provider_name,
                original_error=exc,
            ) from exc

    def get_supported_formats(self) -> list[str]:
        """Formats accepted by OpenAI audio APIs."""
        return ["mp3", "wav", "m4a", "flac", "ogg", "webm", "mp4", "mpeg", "mpga"]

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": [
                "multilingual_transcription",
                "translation",
                "whisper",
                "auto_language_detection",
            ],
        }

    def _prepare_audio(self, audio: bytes | Path) -> tuple[io.BytesIO, float]:
        """Prepara un stream para enviarlo a OpenAI y estima duración."""
        if isinstance(audio, Path):
            raw_audio = audio.read_bytes()
            # Intentar detectar extensión del archivo
            file_extension = audio.suffix.lstrip(".") or "mp3"
        else:
            raw_audio = audio
            # Por defecto usar mp3 si no hay información de extensión
            file_extension = "mp3"

        # Crear un objeto file-like con nombre de archivo
        file = io.BytesIO(raw_audio)
        file.name = f"audio.{file_extension}"
        file.seek(0)

        estimated_duration = len(raw_audio) / 32000
        return file, estimated_duration

    def _build_result(
        self,
        response: Any,
        language: str | None,
        temperature: float,
        duration_hint: float,
        translation_mode: bool,
    ) -> TranscriptionResult:
        """Construye un TranscriptionResult a partir del response de OpenAI."""
        text = getattr(response, "text", "") or ""
        detected_language = getattr(response, "language", language or "und") or language or "und"
        confidence = getattr(response, "confidence", None)
        duration = getattr(response, "duration", duration_hint) or duration_hint

        metadata = {
            "model": self.model,
            "temperature": temperature,
            "translation_mode": translation_mode,
        }

        return TranscriptionResult(
            text=text,
            language=detected_language,
            confidence=confidence,
            provider=self.provider_name,
            duration_seconds=duration,
            metadata=metadata,
        )
