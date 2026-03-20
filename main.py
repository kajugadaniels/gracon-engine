from fastapi import FastAPI # type: ignore
from fastapi.exceptions import RequestValidationError # type: ignore
from botocore.exceptions import ClientError # type: ignore
from app.api.router import api_router
from app.exceptions.handlers import (
    validation_exception_handler,
    aws_exception_handler,
    generic_exception_handler,
)
from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()


def create_app() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI app.
    Using a factory function makes the app easier to test.
    """
    app = FastAPI(
        title="ID Verification Engine",
        description=(
            "Internal AI engine for face comparison and liveness detection. "
            "Not publicly accessible — requires X-Engine-API-Key header."
        ),
        version="1.0.0",
        # Disable docs in production — no need to expose API schema publicly
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url="/redoc" if settings.APP_ENV == "development" else None,
    )

    # ── Register global exception handlers
    # These catch errors from any endpoint and return clean JSON responses
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ClientError, aws_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── Mount all API routes
    app.include_router(api_router)

    # ── Startup event — log configuration summary
    @app.on_event("startup")
    async def startup():
        logger.info(f"Engine starting — environment: {settings.APP_ENV}")
        logger.info(f"AWS region: {settings.AWS_REGION}")
        logger.info(f"S3 bucket: {settings.AWS_S3_BUCKET_NAME}")
        logger.info(
            f"Thresholds — face: {settings.FACE_SIMILARITY_THRESHOLD} "
            f"liveness: {settings.LIVENESS_THRESHOLD} "
            f"composite: {settings.COMPOSITE_PASS_THRESHOLD}"
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level="debug" if settings.APP_ENV == "development" else "info",
    )