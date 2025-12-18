from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LQBOT_",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
    )

    app_name: str = Field(default="lq-bot", description="Nombre de la aplicación")
    environment: str = Field(default="local", description="Entorno de ejecución")
    log_level: str = Field(default="INFO", description="Nivel de logging")

    llm_provider: str = Field(
        default="openai", description="Proveedor LLM por defecto (openai, grok, anthropic)"
    )

    openai_api_key: str = Field(default="", description="API Key de OpenAI")
    openai_llm_model: str = Field(default="gpt-4o-mini", description="Modelo LLM de OpenAI")

    grok_api_key: str = Field(default="", description="API Key de Grok (X.AI)")
    grok_llm_model: str = Field(default="grok-beta", description="Modelo de Grok")
    grok_base_url: str = Field(default="https://api.x.ai/v1", description="Base URL de Grok API")

    tts_provider: str = Field(
        default="openai", description="Proveedor TTS por defecto (openai, elevenlabs)"
    )

    openai_tts_model: str = Field(default="tts-1", description="Modelo TTS de OpenAI")
    openai_tts_voice: str = Field(default="alloy", description="Voz TTS de OpenAI")

    elevenlabs_api_key: str = Field(default="", description="API Key de Eleven Labs")
    elevenlabs_voice_id: str = Field(
        default="21m00Tcm4TlvDq8ikWAM", description="ID de la voz de Eleven Labs (default: Rachel)"
    )
    elevenlabs_tts_model: str = Field(
        default="eleven_multilingual_v2", description="Modelo TTS de Eleven Labs"
    )

    stt_provider: str = Field(
        default="openai", description="Proveedor STT por defecto (openai, elevenlabs)"
    )

    openai_stt_model: str = Field(
        default="gpt-4o-mini-transcribe", description="Modelo STT de OpenAI"
    )

    elevenlabs_stt_model: str = Field(
        default="scribe-v2-realtime", description="Modelo STT de Eleven Labs Scribe v2"
    )
    elevenlabs_stt_language: str = Field(default="en", description="Idioma para Eleven Labs STT")

    storage_provider: str = Field(
        default="boto3", description="Proveedor de storage por defecto (boto3)"
    )

    api_key: str = Field(
        default="", description="API Key para autenticación de endpoints de LQ Bot"
    )
    aws_access_key_id: str = Field(default="access_key", description="AWS Access Key ID")
    aws_secret_access_key: str = Field(default="access_key", description="AWS Secret Access Key")
    aws_region_name: str = Field(default="us-east-1", description="AWS Region")
    s3_endpoint_url: str | None = Field(
        default=None, description="S3 Endpoint URL (None para AWS S3, URL para DO Spaces)"
    )
    s3_default_bucket: str | None = Field(default=None, description="Bucket por defecto")
    s3_max_attempts: int = Field(default=3, description="Número máximo de reintentos")
    s3_connect_timeout: int = Field(default=5, description="Timeout de conexión en segundos")
    s3_read_timeout: int = Field(default=60, description="Timeout de lectura en segundos")

    scenario_multi_agent: bool = Field(
        default=True, description="Usar multi-agent manager para creación de escenarios"
    )


settings = Settings()
