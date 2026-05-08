import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "Second Hand Market API"
    API_V1_STR: str = "/v1"

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # File Uploads
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    # Wallet
    ALLOW_SELF_RECHARGE: bool = True
    MAX_SELF_RECHARGE_AMOUNT: int = 1000000  # Max 10,000 yuan per recharge (in cents)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Auto-generate SECRET_KEY if not set (prevents the insecure placeholder problem)
if not settings.SECRET_KEY or settings.SECRET_KEY == "replace_me_with_something_secure":
    settings.SECRET_KEY = secrets.token_urlsafe(32)
    print("WARNING: SECRET_KEY was not set or used the placeholder. A random key has been generated for this session.")
    print("Please set a permanent SECRET_KEY in your .env file for production use.")

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
