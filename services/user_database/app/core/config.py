from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # model_config allows loading from a .env file
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Asynchronous database connection URL
    # Example: "postgresql+asyncpg://user:password@host:port/dbname"
    DATABASE_URL: str


settings = Settings()
