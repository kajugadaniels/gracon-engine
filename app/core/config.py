from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    All configuration loaded from .env file.
    pydantic-settings validates types automatically —
    missing required vars raise an error at startup, not at runtime.
    """

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    # Internal security — NestJS must send this key in every request
    ENGINE_API_KEY: str

    # AWS credentials — used for both S3 and Rekognition
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str

    # Scoring thresholds — tunable without code changes
    FACE_SIMILARITY_THRESHOLD: float = 70.0
    LIVENESS_THRESHOLD: float = 70.0
    COMPOSITE_PASS_THRESHOLD: float = 80.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True  # env vars must match exactly


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance — loaded once at startup.
    lru_cache ensures .env is only read once, not on every request.
    """
    return Settings()