import boto3
from botocore.config import Config
from functools import lru_cache
from app.core.config import get_settings
from app.core.logging import logger


@lru_cache()
def get_rekognition_client():
    """
    Creates and caches a single Rekognition client for the app lifetime.
    Uses REKOGNITION_REGION — separate from AWS_REGION (S3) because
    Rekognition is not available in all regions (e.g. eu-north-1).
    """
    settings = get_settings()

    config = Config(
        region_name=settings.AWS_REGION,
        retries={
            "max_attempts": 3,
            "mode": "adaptive",
        },
        connect_timeout=5,
        read_timeout=30,
    )

    client = boto3.client(
        "rekognition",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=config,
    )

    logger.info(f"Rekognition client created for region: {settings.AWS_REGION}")
    return client


@lru_cache()
def get_s3_client():
    """
    Creates and caches a single S3 client.
    Used to fetch images from S3 before passing to Rekognition.
    """
    settings = get_settings()

    config = Config(
        region_name=settings.AWS_REGION,
        retries={"max_attempts": 3, "mode": "adaptive"},
        connect_timeout=5,
        read_timeout=15,
    )

    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=config,
    )

    logger.info(f"S3 client created for region: {settings.AWS_REGION}")
    return client