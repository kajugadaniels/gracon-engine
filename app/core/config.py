from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    All configuration loaded from environment variables (or .env file in development).
    pydantic-settings validates types and required fields at startup —
    missing required vars raise a clear error before the app accepts any requests.
    """

    model_config = SettingsConfigDict(
        env_file=".env",           # used in development; ignored if the file is absent
        env_file_encoding="utf-8",
        case_sensitive=True,       # AWS_REGION ≠ aws_region
        extra="ignore",            # silently ignore unknown vars from the environment
    )

    # App
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    # Internal security — NestJS gateway must send this key in every request
    ENGINE_API_KEY: str

    # AWS credentials
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str

    # Scoring thresholds — tunable per environment without code changes
    FACE_SIMILARITY_THRESHOLD: float = 70.0
    LIVENESS_THRESHOLD: float = 70.0
    COMPOSITE_PASS_THRESHOLD: float = 80.0


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance — loaded and validated once at startup.
    lru_cache ensures the env file is only read once, not on every request.
    """
    return Settings()
