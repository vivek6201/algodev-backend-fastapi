from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Algorithmic Dev"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    DOMAIN: Optional[str] = "localhost"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = ""

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    # Email (optional)
    RESEND_API_KEY: Optional[str] = None

    # AWS
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_CLOUDFRONT_DOMAIN: Optional[str] = None
    AWS_CLOUDFRONT_KEYPAIR_ID: Optional[str] = None
    AWS_CLOUDFRONT_PRIVATE_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://192.168.1.8:3000",
        "http://192.168.1.8:3001",
    ]
    TRUSTED_HOSTS: list[str] = ["localhost", "127.0.0.1", "::1", "192.168.1.8"]

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


# Create settings instance
settings = Settings()
