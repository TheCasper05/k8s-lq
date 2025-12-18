from typing import Any, Literal

from openai import AsyncOpenAI

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.audio import AudioOutput, VoiceConfig
from src.domain.ports.ai.tts_port import TTSPort


class OpenAITTSAdapter(TTSPort):
    """Adaptador TTS que consume la API de OpenAI Speech."""

    def __init__(self, api_key: str, model: str = "tts-1", voice: str = "alloy"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_voice = voice
        self.provider_name = "openai"

    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        # language: str = "en",
        audio_format: Literal["wav", "mp3", "ogg"] = "wav",
        speed: float = 1.0,
        **kwargs: Any,
    ) -> AudioOutput:
        """Genera audio con la voz solicitada."""
        try:
            selected_voice = self.default_voice if voice == "default" else voice
            params: dict[str, Any] = {
                "model": self.model,
                "voice": selected_voice,
                "input": text,
                # "language": language,
                "response_format": self._map_format(audio_format),
            }
            params.update(kwargs)

            response = await self.client.audio.speech.create(**params)
            audio_bytes = self._extract_audio_bytes(response)
            estimated_duration = len(audio_bytes) / 24000

            return AudioOutput(
                audio_data=audio_bytes,
                format=audio_format,
                duration_seconds=estimated_duration,
                voice_used=selected_voice,
                provider=self.provider_name,
                metadata={
                    "model": self.model,
                    # "language": language,
                    "speed": speed,
                    "extra": kwargs,
                },
            )

        except Exception as exc:
            print(exc)
            raise AIProviderError(
                "Error al sintetizar audio con OpenAI",
                provider=self.provider_name,
                original_error=exc,
            ) from exc

    async def get_available_voices(self, language: str | None = None) -> list[VoiceConfig]:
        """Obtiene la lista de voces soportadas, usando la API si está disponible."""
        voices_endpoint = getattr(self.client.audio.speech, "list_voices", None)
        try:
            voice_data = []
            if voices_endpoint:
                response = await voices_endpoint()
                voice_data = getattr(response, "data", []) or []

            if not voice_data:
                voice_data = self._default_voice_catalog()

            result = []
            for voice in voice_data:
                voice_id = str(
                    voice.get("id") or voice.get("voice_id") or voice.get("name") or "unknown_voice"
                )
                result.append(
                    VoiceConfig(
                        id=voice_id,
                        name=voice.get("name", voice_id),
                        language=voice.get("language", "multilingual"),
                        gender=voice.get("gender", "neutral"),
                        provider=self.provider_name,
                    )
                )
            if language:
                result = [
                    voice
                    for voice in result
                    if voice.language.lower().startswith(language.lower())
                    or voice.language == "multilingual"
                ]
            return result
        except Exception as exc:
            raise AIProviderError(
                "No se pudo obtener la lista de voces de OpenAI",
                provider=self.provider_name,
                original_error=exc,
            ) from exc

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": ["high_quality_tts", "multilingual", "voice_selection"],
        }

    def _map_format(self, audio_format: Literal["wav", "mp3", "ogg"]) -> str:
        """Ajusta el formato para la API de OpenAI."""
        mapping = {"wav": "wav", "mp3": "mp3", "ogg": "ogg"}
        return mapping.get(audio_format, "wav")

    def _extract_audio_bytes(self, response: Any) -> bytes:
        """Obtiene los bytes del objeto de respuesta de OpenAI."""
        if isinstance(response, (bytes, bytearray)):
            return bytes(response)
        if hasattr(response, "audio"):
            return response.audio
        if hasattr(response, "content"):
            return response.content
        raise AIProviderError(
            "Respuesta de OpenAI no contiene audio valido",
            provider=self.provider_name,
        )

    def _default_voice_catalog(self) -> list[dict[str, Any]]:
        """Lista base de voces cuando el endpoint no está disponible."""
        return [
            {"id": "alloy", "name": "Alloy", "language": "multilingual", "gender": "neutral"},
            {"id": "atticus", "name": "Atticus", "language": "en", "gender": "male"},
            {"id": "luna", "name": "Luna", "language": "es", "gender": "female"},
        ]
