from dataclasses import dataclass
from typing import Optional
from app.services.rekognition.face_comparison import FaceComparisonResult
from app.services.rekognition.liveness import LivenessResult
from app.core.config import get_settings
from app.core.logging import logger


@dataclass
class CompositeScore:
    """
    Final composite score combining all verification signals.
    Returned to the NestJS gateway for storage and response.
    """
    face_score: float         # raw face similarity 0-100
    liveness_score: float     # raw liveness confidence 0-100
    document_match: bool      # exact NID match — binary
    composite_score: float    # weighted final score 0-100
    passed: bool              # composite >= threshold AND document matched
    fail_reason: Optional[str] # human-readable reason if failed


# Scoring weights — must sum to 1.0
FACE_WEIGHT = 0.50      # face similarity contributes 50%
LIVENESS_WEIGHT = 0.30  # liveness confidence contributes 30%
DOCUMENT_WEIGHT = 0.20  # document match contributes 20% (binary: 0 or full)


def calculate_composite_score(
    face_result: FaceComparisonResult,
    liveness_result: LivenessResult,
    document_match: bool,
) -> CompositeScore:
    """
    Calculates the final composite verification score.

    Scoring rules:
    1. If document_match is False → immediate fail (score=0), no further checks
    2. If no face found in either image → fail with quality message
    3. Otherwise → weighted composite of face + liveness + document

    Weight breakdown:
    - Face similarity:  50% (core identity check)
    - Liveness:         30% (anti-spoofing)
    - Document match:   20% (binary — full 20 points or 0)

    Pass threshold: composite >= COMPOSITE_PASS_THRESHOLD (default 80%)
    """
    settings = get_settings()

    # ── Rule 1: Document must match — hard gate, no exceptions
    if not document_match:
        logger.warning("Verification failed: document number mismatch")
        return CompositeScore(
            face_score=face_result.similarity,
            liveness_score=liveness_result.confidence,
            document_match=False,
            composite_score=0.0,
            passed=False,
            fail_reason="The National ID number entered does not match our records. Please ensure you entered your ID number correctly.",
        )

    # ── Rule 2: Face must be detected in both images
    if not face_result.face_found_in_id:
        logger.warning("Verification failed: no face detected in ID card image")
        return CompositeScore(
            face_score=0.0,
            liveness_score=liveness_result.confidence,
            document_match=document_match,
            composite_score=0.0,
            passed=False,
            fail_reason=f"No face could be detected in your ID card photo. Please ensure your ID card is clearly visible and well-lit. Image quality: {face_result.id_image_quality}",
        )

    if not face_result.face_found_in_selfie:
        logger.warning("Verification failed: no face detected in selfie")
        return CompositeScore(
            face_score=0.0,
            liveness_score=liveness_result.confidence,
            document_match=document_match,
            composite_score=0.0,
            passed=False,
            fail_reason=f"No face could be detected in your selfie. Please ensure your face is clearly visible, centred, and well-lit. Image quality: {face_result.selfie_quality}",
        )

    # ── Rule 3: Liveness must pass minimum threshold
    if liveness_result.confidence < settings.LIVENESS_THRESHOLD:
        logger.warning(
            f"Verification failed: liveness score too low ({liveness_result.confidence:.1f})"
        )
        return CompositeScore(
            face_score=face_result.similarity,
            liveness_score=liveness_result.confidence,
            document_match=document_match,
            composite_score=liveness_result.confidence * LIVENESS_WEIGHT,
            passed=False,
            fail_reason="Liveness check failed. Please ensure you are taking a real selfie in good lighting, not a photo of a photo.",
        )

    # ── Step 4: Calculate weighted composite score
    # Document match is binary: full 20 points (100 * 0.20) or 0
    document_contribution = 100.0 * DOCUMENT_WEIGHT  # = 20.0 points

    composite = (
        (face_result.similarity * FACE_WEIGHT) +
        (liveness_result.confidence * LIVENESS_WEIGHT) +
        document_contribution
    )

    composite = round(min(100.0, max(0.0, composite)), 2)
    passed = composite >= settings.COMPOSITE_PASS_THRESHOLD

    # Build failure reason for borderline fails
    fail_reason = None
    if not passed:
        fail_reason = _build_fail_reason(
            face_result.similarity,
            liveness_result.confidence,
            composite,
            settings.COMPOSITE_PASS_THRESHOLD,
        )

    logger.info(
        f"Composite score: {composite:.1f} | "
        f"face={face_result.similarity:.1f} liveness={liveness_result.confidence:.1f} "
        f"doc={document_match} | passed={passed}"
    )

    return CompositeScore(
        face_score=face_result.similarity,
        liveness_score=liveness_result.confidence,
        document_match=document_match,
        composite_score=composite,
        passed=passed,
        fail_reason=fail_reason,
    )


def _build_fail_reason(
    face_score: float,
    liveness_score: float,
    composite: float,
    threshold: float,
) -> str:
    """
    Builds a specific, actionable failure message based on which
    scores were weakest — helps the user understand what to improve.
    """
    issues = []

    if face_score < 60:
        issues.append(
            "The face on your ID card could not be confidently matched to your selfie "
            f"(similarity: {face_score:.0f}%). Ensure both images are clear and well-lit."
        )

    if liveness_score < 70:
        issues.append(
            "The selfie did not fully pass the liveness check. "
            "Please take a fresh selfie in good lighting, looking directly at the camera."
        )

    if not issues:
        issues.append(
            f"Your verification score ({composite:.0f}%) was below the required threshold ({threshold:.0f}%). "
            "Please retake both photos in good lighting with your face clearly visible."
        )

    return " ".join(issues)