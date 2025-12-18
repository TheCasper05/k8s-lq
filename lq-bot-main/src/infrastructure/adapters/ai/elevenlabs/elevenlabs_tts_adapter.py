"""Adaptador TTS para Eleven Labs."""

from typing import Any, Literal

import httpx

from src.domain.exceptions.ai_exceptions import AIProviderError
from src.domain.models.audio import AudioOutput, VoiceConfig
from src.domain.ports.ai.tts_port import TTSPort


class ElevenLabsTTSAdapter(TTSPort):
    """
    Implementación del port TTS usando Eleven Labs.

    Eleven Labs ofrece TTS de alta calidad con voces muy naturales
    y soporte para múltiples idiomas.

    API Doc: https://elevenlabs.io/docs/api-reference/text-to-speech
    """

    def __init__(
        self,
        api_key: str,
        model: str = "eleven_multilingual_v2",
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel (default)
    ):
        """
        Inicializa el adaptador de Eleven Labs TTS.

        Args:
            api_key: API key de Eleven Labs
            model: Modelo TTS a usar
            voice_id: ID de la voz por defecto
        """
        self.api_key = api_key
        self.model = model
        self.default_voice_id = voice_id
        self.provider_name = "elevenlabs"
        self.base_url = "https://api.elevenlabs.io/v1"

    async def synthesize_speech(
        self,
        text: str,
        voice: str = "default",
        language: str = "en",
        audio_format: Literal["wav", "mp3", "ogg"] = "mp3",
        speed: float = 1.0,
        **kwargs,
    ) -> AudioOutput:
        """
        Convierte texto a audio usando Eleven Labs.

        Args:
            text: Texto a sintetizar
            voice: ID de la voz o "default" para usar la configurada
            language: Código de idioma (no usado directamente, el modelo es multiidioma)
            audio_format: Formato de salida (mp3, wav, ogg)
            speed: Velocidad de reproducción (ajustado via stability/similarity_boost)
            **kwargs: Parámetros adicionales (stability, similarity_boost, style, etc.)

        Returns:
            AudioOutput con el audio generado

        Raises:
            AIProviderError: Si hay error en la síntesis
        """
        try:
            # Determinar voice ID
            voice_id = self.default_voice_id if voice == "default" else voice

            # URL del endpoint
            url = f"{self.base_url}/text-to-speech/{voice_id}"

            # Headers
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
            }

            # Mapear formato de audio
            output_format = self._map_audio_format(audio_format)

            # Configuración de voz
            voice_settings = {
                "stability": kwargs.get("stability", 0.5),
                "similarity_boost": kwargs.get("similarity_boost", 0.75),
            }

            # Si se especifica style o use_speaker_boost
            if "style" in kwargs:
                voice_settings["style"] = kwargs["style"]
            if "use_speaker_boost" in kwargs:
                voice_settings["use_speaker_boost"] = kwargs["use_speaker_boost"]

            # Payload
            payload = {
                "text": text,
                "model_id": self.model,
                "voice_settings": voice_settings,
            }

            # Parámetros de query
            params = {
                "output_format": output_format,
            }

            # Hacer request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload, params=params)
                response.raise_for_status()

            # El response es directamente el audio en bytes
            audio_data = response.content

            # Estimar duración (aproximación basada en tamaño)
            estimated_duration = len(audio_data) / 24000  # ~24KB por segundo para MP3

            return AudioOutput(
                audio_data=audio_data,
                format=audio_format,
                duration_seconds=estimated_duration,
                voice_used=voice_id,
                provider=self.provider_name,
                metadata={
                    "model": self.model,
                    "voice_settings": voice_settings,
                    "text_length": len(text),
                },
            )

        except httpx.HTTPStatusError as e:
            raise AIProviderError(
                f"Error HTTP de Eleven Labs TTS: {e.response.status_code} - {e.response.text}",
                provider=self.provider_name,
                original_error=e,
            ) from e
        except Exception as e:
            raise AIProviderError(
                f"Error en Eleven Labs TTS: {e!s}", provider=self.provider_name, original_error=e
            ) from e

    async def get_available_voices(self, language: str | None = None) -> list[VoiceConfig]:
        """
        Obtiene lista de voces disponibles de Eleven Labs.

        Args:
            language: Filtro por idioma (Eleven Labs voces son multiidioma)

        Returns:
            Lista de VoiceConfig con las voces disponibles
        """
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

            data = response.json()
            voices = []

            for voice in data.get("voices", []):
                # Eleven Labs no especifica género explícitamente en la API
                # Se podría inferir del nombre o descripción
                voices.append(
                    VoiceConfig(
                        id=voice["voice_id"],
                        name=voice["name"],
                        language="multilingual",  # Todas las voces son multiidioma
                        gender="neutral",  # Sin info explícita
                        provider=self.provider_name,
                    )
                )

            return voices

        except Exception as e:
            raise AIProviderError(
                f"Error obteniendo voces de Eleven Labs: {e!s}",
                provider=self.provider_name,
                original_error=e,
            ) from e

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_model_info(self) -> dict[str, Any]:
        """Retorna información del modelo TTS."""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "capabilities": [
                "high_quality_tts",
                "multilingual",
                "voice_cloning",
                "emotion_control",
            ],
            "supported_formats": ["mp3", "wav", "ogg", "flac", "pcm"],
        }

    def _map_audio_format(self, format: Literal["wav", "mp3", "ogg"]) -> str:
        """Mapea formato interno a formato de Eleven Labs API."""
        format_map = {
            "mp3": "mp3_44100_128",
            "wav": "pcm_44100",
            "ogg": "ogg_44100_128",
        }
        return format_map.get(format, "mp3_44100_128")
