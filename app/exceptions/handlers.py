from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from botocore.exceptions import BotoCoreError, ClientError
from app.core.logging import logger


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handles Pydantic validation errors — returns clean 422 with field details.
    Never exposes internal field names that could help an attacker.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "errors": errors},
    )


async def aws_exception_handler(
    request: Request,
    exc: ClientError,
) -> JSONResponse:
    """
    Handles AWS ClientError exceptions that bubble up from services.
    Logs full details server-side, returns safe message to caller.
    """
    error_code = exc.response["Error"]["Code"]
    logger.error(f"Unhandled AWS ClientError: {error_code} on {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": "AWS service temporarily unavailable. Please try again.",
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch-all handler — ensures no stack traces leak to the caller.
    Always logs full details server-side.
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected error occurred. Please try again.",
        },
    )