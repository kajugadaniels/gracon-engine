from pydantic import BaseModel, Field
from typing import Optional


class ScoreBreakdown(BaseModel):
    """
    Individual sub-scores that make up the composite score.
    Returned to the gateway so it can store each score separately.
    """
    face_similarity: float = Field(..., ge=0, le=100, description="Rekognition CompareFaces similarity score")
    liveness_confidence: float = Field(..., ge=0, le=100, description="Rekognition FaceLiveness confidence score")
    document_match: bool = Field(..., description="Whether typed NID matched stored NID")
    composite_score: float = Field(..., ge=0, le=100, description="Weighted final score")


class VerificationResponse(BaseModel):
    """
    Full response returned to the NestJS gateway after verification.
    Gateway stores this in the id_verifications table.
    """
    passed: bool = Field(..., description="True if composite score >= threshold AND document matched")
    scores: ScoreBreakdown
    fail_reason: Optional[str] = Field(None, description="Human-readable reason if verification failed")

    # Image quality flags — helps frontend give better user instructions
    id_image_quality: str = Field(..., description="good | blurry | no_face | too_dark")
    selfie_quality: str = Field(..., description="good | blurry | no_face | too_dark")


class HealthResponse(BaseModel):
    """Response for the health check endpoint."""
    status: str
    environment: str
    aws_connected: bool