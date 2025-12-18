"""
Configuration module for LQ Real-time Service.
Loads settings from environment variables with sensible defaults.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="lq-realtime-service", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="production", description="Environment name")

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8082, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")

    jwt_secret_key: str = Field(
        default="change-me-in-production-min-32-chars",
        description="JWT secret key for signing tokens",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=15, description="JWT token expiration in minutes"
    )

    system_api_key: str = Field(
        default="change-me-system-api-key-min-32-chars",
        description="API key for system-level operations (global broadcasts)",
    )

    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str = Field(default="", description="Redis password")
    redis_max_connections: int = Field(default=100, description="Redis max connection pool size")

    ws_max_connections_per_instance: int = Field(
        default=10000, description="Maximum concurrent WebSocket connections per instance"
    )
    ws_heartbeat_interval: int = Field(
        default=30, description="WebSocket heartbeat interval in seconds"
    )
    ws_message_max_size: int = Field(
        default=65536, description="Maximum WebSocket message size in bytes"
    )

    webhook_max_retries: int = Field(default=3, description="Maximum webhook retry attempts")
    webhook_retry_delay: int = Field(default=5, description="Webhook retry delay in seconds")
    webhook_timeout: int = Field(default=30, description="Webhook timeout in seconds")

    allowed_origins: str = Field(
        default="http://localhost:3000", description="Comma-separated allowed CORS origins"
    )
    cors_enabled: bool = Field(default=True, description="Enable CORS")

    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    metrics_enabled: bool = Field(default=True, description="Enable metrics endpoint")
    health_check_path: str = Field(default="/health", description="Health check endpoint path")

    @field_validator("allowed_origins")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins into a list."""
        if not v:
            return []
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures we load settings only once.
    """
    return Settings()
