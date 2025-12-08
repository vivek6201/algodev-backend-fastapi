from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Algorithmic Dev"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    DOMAIN: str = "localhost"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = ""

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1", "::1"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


# Create settings instance
settings = Settings()
