"""Application settings via pydantic-settings. All secrets from env vars."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (no default — must be set via env var)
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # JWT (no default — must be set via env var)
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480  # 8 hours

    # Azure Storage
    azure_storage_connection_string: str = ""
    azure_storage_container_name: str = "amcas-uploads"

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # Application
    environment: str = "development"
    log_level: str = "info"

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
