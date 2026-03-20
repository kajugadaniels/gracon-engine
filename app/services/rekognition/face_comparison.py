import boto3
from botocore.exceptions import ClientError
from dataclasses import dataclass
from typing import Optional
from app.services.rekognition.client import get_rekognition_client, get_s3_client
from app.core.config import get_settings
from app.core.logging import logger


@dataclass
class FaceComparisonResult:
    """Result from CompareFaces API call."""
    similarity: float           # 0-100 — how similar the two faces are
    face_found_in_id: bool      # was a face detected in the ID card image
    face_found_in_selfie: bool  # was a face detected in the selfie
    id_image_quality: str       # good | blurry | no_face | too_dark
    selfie_quality: str         # good | blurry | no_face | too_dark
    error: Optional[str] = None # set if AWS call failed


def compare_faces(id_image_key: str, selfie_image_key: str) -> FaceComparisonResult:
    """
    Compares the face on an ID card photo against a selfie using
    AWS Rekognition CompareFaces API.

    Both images are referenced by their S3 keys — Rekognition pulls
    them directly from S3 using the engine's IAM permissions.

    Returns a FaceComparisonResult with similarity score and quality flags.
    """
    settings = get_settings()
    rekognition = get_rekognition_client()

    try:
        response = rekognition.compare_faces(
            SourceImage={
                # ID card photo — the reference face
                "S3Object": {
                    "Bucket": settings.AWS_S3_BUCKET_NAME,
                    "Name": id_image_key,
                }
            },
            TargetImage={
                # Selfie — the face to compare against
                "S3Object": {
                    "Bucket": settings.AWS_S3_BUCKET_NAME,
                    "Name": selfie_image_key,
                }
            },
            SimilarityThreshold=0,   # return all matches, we apply our own threshold
            QualityFilter="MEDIUM",  # filter out very low quality face detections
        )

        # Extract face matches — list of faces in selfie that match the ID face
        face_matches = response.get("FaceMatches", [])
        unmatched_faces = response.get("UnmatchedFaces", [])
        source_image_face = response.get("SourceImageFace", {})

        # Determine if faces were found
        face_found_in_id = source_image_face is not None and bool(source_image_face)
        face_found_in_selfie = len(face_matches) > 0 or len(unmatched_faces) > 0

        # Get similarity score — take highest if multiple matches (shouldn't happen)
        similarity = 0.0
        if face_matches:
            similarity = max(
                match.get("Similarity", 0.0) for match in face_matches
            )

        # Assess image quality from Rekognition quality indicators
        id_quality = _assess_image_quality(source_image_face, face_found_in_id)
        selfie_face = face_matches[0].get("Face", {}) if face_matches else (
            unmatched_faces[0] if unmatched_faces else {}
        )
        selfie_quality = _assess_image_quality(selfie_face, face_found_in_selfie)

        logger.info(
            f"Face comparison complete — similarity: {similarity:.1f}% "
            f"| id_face: {face_found_in_id} | selfie_face: {face_found_in_selfie}"
        )

        return FaceComparisonResult(
            similarity=round(similarity, 2),
            face_found_in_id=face_found_in_id,
            face_found_in_selfie=face_found_in_selfie,
            id_image_quality=id_quality,
            selfie_quality=selfie_quality,
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Rekognition CompareFaces failed: {error_code} — {str(e)}")

        # Handle specific error types with helpful messages
        if error_code == "InvalidParameterException":
            # Usually means no face detected in one of the images
            return FaceComparisonResult(
                similarity=0.0,
                face_found_in_id=False,
                face_found_in_selfie=False,
                id_image_quality="no_face",
                selfie_quality="no_face",
                error="No face detected in one or both images",
            )

        if error_code == "ImageTooLargeException":
            return FaceComparisonResult(
                similarity=0.0,
                face_found_in_id=False,
                face_found_in_selfie=False,
                id_image_quality="good",
                selfie_quality="good",
                error="Image file too large — maximum 5MB per image",
            )

        return FaceComparisonResult(
            similarity=0.0,
            face_found_in_id=False,
            face_found_in_selfie=False,
            id_image_quality="good",
            selfie_quality="good",
            error=f"AWS error: {error_code}",
        )


def _assess_image_quality(face_detail: dict, face_found: bool) -> str:
    """
    Assesses image quality based on Rekognition face quality indicators.
    Returns one of: good | blurry | no_face | too_dark
    """
    if not face_found or not face_detail:
        return "no_face"

    quality = face_detail.get("Quality", {})
    brightness = quality.get("Brightness", 100)
    sharpness = quality.get("Sharpness", 100)

    if sharpness < 20:
        return "blurry"

    if brightness < 20:
        return "too_dark"

    return "good"