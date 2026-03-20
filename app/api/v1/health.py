from fastapi import APIRouter # type: ignore
from app.models.responses import HealthResponse
from app.services.rekognition.client import get_rekognition_client
from app.core.config import get_settings
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Checks if the engine is running and AWS is reachable.",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint — called by NestJS before sending verification requests.
    Verifies AWS connectivity by calling a lightweight Rekognition API.
    No API key required — used by load balancers and monitoring tools.
    """
    settings = get_settings()
    aws_connected = False

    try:
        # list_collections is a lightweight call that confirms AWS connectivity
        rekognition = get_rekognition_client()
        rekognition.list_collections(MaxResults=1)
        aws_connected = True
    except Exception as e:
        logger.warning(f"Health check: AWS connectivity issue — {str(e)}")

    return HealthResponse(
        status="ok" if aws_connected else "degraded",
        environment=settings.APP_ENV,
        aws_connected=aws_connected,
    )