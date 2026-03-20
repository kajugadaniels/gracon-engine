from fastapi import APIRouter # type: ignore
from app.api.v1.verification import router as verification_router
from app.api.v1.health import router as health_router

# Main API router — mounts all v1 endpoints under /api/v1
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(verification_router, tags=["Verification"])
api_router.include_router(health_router, tags=["Health"])