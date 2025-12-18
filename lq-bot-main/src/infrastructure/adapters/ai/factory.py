"""Factory para crear adaptadores de proveedores de IA."""

from src.config import Settings
from src.domain.ports.ai.llm_port import LLMPort
from src.domain.ports.ai.stt_port import STTPort
from src.domain.ports.ai.tts_port import TTSPort
from src.infrastructure.adapters.ai.elevenlabs.elevenlabs_stt_adapter import ElevenLabsSTTAdapter
from src.infrastructure.adapters.ai.elevenlabs.elevenlabs_tts_adapter import ElevenLabsTTSAdapter
from src.infrastructure.adapters.ai.grok.grok_llm_adapter import GrokLLMAdapter
from src.infrastructure.adapters.ai.openai.openai_llm_adapter import OpenAILLMAdapter
from src.infrastructure.adapters.ai.openai.openai_stt_adapter import OpenAISTTAdapter
from src.infrastructure.adapters.ai.openai.openai_tts_adapter import OpenAITTSAdapter


class AIProviderFactory:
    """Factory para crear adaptadores de proveedores de AI."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def create_llm_adapter(self, provider: str | None = None) -> LLMPort:
        """
        Crea un adaptador LLM según el proveedor especificado.

        Args:
            provider: Nombre del proveedor (openai, grok, anthropic).
                     Si es None, usa el configurado en settings.llm_provider

        Returns:
            Adaptador LLM implementando LLMPort

        Raises:
            ValueError: Si el proveedor no está soportado
        """
        provider = provider or self.settings.llm_provider

        if provider == "openai":
            return OpenAILLMAdapter(
                api_key=self.settings.openai_api_key, model=self.settings.openai_llm_model
            )

        elif provider == "grok":
            return GrokLLMAdapter(
                api_key=self.settings.grok_api_key,
                model=self.settings.grok_llm_model,
                base_url=self.settings.grok_base_url,
            )

        else:
            raise ValueError(
                f"Proveedor LLM '{provider}' no soportado. Proveedores disponibles: openai, grok"
            )

    def create_tts_adapter(self, provider: str | None = None) -> TTSPort:
        """
        Crea un adaptador TTS según el proveedor especificado.

        Args:
            provider: Nombre del proveedor (openai, elevenlabs).
                     Si es None, usa el configurado en settings.tts_provider

        Returns:
            Adaptador TTS implementando TTSPort

        Raises:
            ValueError: Si el proveedor no está soportado
        """
        provider = provider or self.settings.tts_provider

        if provider == "openai":
            return OpenAITTSAdapter(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_tts_model,
                voice=self.settings.openai_tts_voice,
            )

        elif provider == "elevenlabs":
            return ElevenLabsTTSAdapter(
                api_key=self.settings.elevenlabs_api_key,
                model=self.settings.elevenlabs_tts_model,
                voice_id=self.settings.elevenlabs_voice_id,
            )

        else:
            raise ValueError(
                f"Proveedor TTS '{provider}' no soportado. "
                f"Proveedores disponibles: openai, elevenlabs"
            )

    def create_stt_adapter(self, provider: str | None = None) -> STTPort:
        """
        Crea un adaptador STT según el proveedor especificado.

        Args:
            provider: Nombre del proveedor (openai, elevenlabs).
                     Si es None, usa el configurado en settings.stt_provider

        Returns:
            Adaptador STT implementando STTPort

        Raises:
            ValueError: Si el proveedor no está soportado
        """
        provider = provider or self.settings.stt_provider

        if provider == "openai":
            return OpenAISTTAdapter(
                api_key=self.settings.openai_api_key, model=self.settings.openai_stt_model
            )

        elif provider == "elevenlabs":
            return ElevenLabsSTTAdapter(
                api_key=self.settings.elevenlabs_api_key,
                model=self.settings.elevenlabs_stt_model,
                language=self.settings.elevenlabs_stt_language,
            )

        else:
            raise ValueError(
                f"Proveedor STT '{provider}' no soportado. "
                f"Proveedores disponibles: openai, elevenlabs"
            )
