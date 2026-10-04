"""
Environment configuration using pydantic-settings.

Per project rules:
- Use environment variables for secrets
- Do not commit secrets
- Do not put production credentials in source code
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./counselconnect.db"
    database_url_sync: str = "sqlite:///./counselconnect.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # MinIO (Object Storage)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "counselconnect"
    minio_use_ssl: bool = False

    # Ollama (Local LLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    ollama_timeout_seconds: float = 120.0

    # Authentication
    session_secret: str = "change-me-to-a-random-secret-in-production"

    # Application URLs
    app_origin: str = "http://localhost:3000"
    api_origin: str = "http://localhost:8000"
    cookie_domain: str | None = None

    # Storage limits
    storage_max_file_size_mb: int = 50

    # Environment
    python_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
