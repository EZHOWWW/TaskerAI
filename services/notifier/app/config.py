from pydantic_settings import BaseSettings, SettingsConfigDict

from core_lib.global_logging_config import setup_service_logging

logger = setup_service_logging("user_database")


class Settings(BaseSettings):
    """Manages application settings and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    USER_SERVICE_URL: str = "http://localhost:8001"
    TASK_SERVICE_URL: str = "http://localhost:8002"
    TELEGRAM_BOT_TOKEN: str


settings = Settings()
