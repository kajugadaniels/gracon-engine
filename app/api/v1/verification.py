from fastapi import APIRouter, Depends, HTTPException, status
from app.models.requests import VerificationRequest
from app.models.responses import VerificationResponse, ScoreBreakdown
from app.services.rekognition.face_comparison import compare_faces
from app.services.rekognition.liveness import check_liveness
from app.services.scoring import calculate_composite_score
from app.core.security import verify_api_key
from app.core.config import get_settings
from app.core.logging import logger

router = APIRouter()


@router.post(
    "/verify",
    response_model=VerificationResponse,
    summary="Run face + liveness verification",
    description=(
        "Accepts S3 keys for an ID card image and a selfie. "
        "Runs Rekognition CompareFaces and liveness detection in parallel. "
        "Returns composite score and pass/fail result. "
        "Internal endpoint — requires X-Engine-API-Key header."
    ),
)
async def verify_identity(
    request: VerificationRequest,
    _: str = Depends(verify_api_key),  # validates API key before anything runs
) -> VerificationResponse:
    """
    Main verification endpoint — called only by the NestJS gateway.

    Flow:
    1. Run face comparison (ID card photo vs selfie)
    2. Run liveness detection (selfie only)
    3. Calculate composite score
    4. Return structured result

    Note: document_match is computed by the NestJS gateway
    (it has access to the encrypted NID in the database).
    The gateway passes the result here as a boolean.
    """
    logger.info(
        f"Verification request received for user: {request.user_id} "
        f"| id_key: ...{request.id_image_key[-20:]} "
        f"| selfie_key: ...{request.selfie_image_key[-20:]}"
    )

    # ── Step 1: Run face comparison
    # Rekognition compares face on ID card photo vs selfie
    face_result = compare_faces(
        id_image_key=request.id_image_key,
        selfie_image_key=request.selfie_image_key,
    )

    # ── Step 2: Run liveness detection
    # Assesses whether the selfie is a real live person
    liveness_result = check_liveness(
        selfie_image_key=request.selfie_image_key,
    )

    # ── Step 3: Calculate composite score
    # document_match comes from the request — validated by NestJS gateway
    composite = calculate_composite_score(
        face_result=face_result,
        liveness_result=liveness_result,
        document_match=request.document_match,
    )

    logger.info(
        f"Verification complete for user: {request.user_id} "
        f"| score: {composite.composite_score:.1f} | passed: {composite.passed}"
    )

    return VerificationResponse(
        passed=composite.passed,
        scores=ScoreBreakdown(
            face_similarity=composite.face_score,
            liveness_confidence=composite.liveness_score,
            document_match=composite.document_match,
            composite_score=composite.composite_score,
        ),
        fail_reason=composite.fail_reason,
        id_image_quality=face_result.id_image_quality,
        selfie_quality=face_result.selfie_quality,
    )