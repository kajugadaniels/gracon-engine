from botocore.exceptions import ClientError
from dataclasses import dataclass
from typing import Optional
from app.services.rekognition.client import get_rekognition_client, get_s3_client
from app.core.config import get_settings
from app.core.logging import logger


@dataclass
class LivenessResult:
    """Result from FaceDetect-based liveness analysis."""
    confidence: float           # 0-100 liveness confidence score
    is_live: bool               # confidence >= threshold
    face_detected: bool         # was a face found at all
    error: Optional[str] = None


def _download_image_bytes(s3_client, bucket: str, key: str) -> bytes:
    """Downloads an image from S3 and returns its raw bytes."""
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


def check_liveness(selfie_image_key: str) -> LivenessResult:
    """
    Performs liveness detection on a selfie image using AWS Rekognition.

    Image is downloaded from S3 (eu-north-1) as bytes and passed directly
    to Rekognition (eu-west-1) — required because Rekognition S3Object
    references only work when bucket and Rekognition are in the same region.
    """
    settings = get_settings()
    rekognition = get_rekognition_client()
    s3 = get_s3_client()

    try:
        selfie_bytes = _download_image_bytes(s3, settings.AWS_S3_BUCKET_NAME, selfie_image_key)

        response = rekognition.detect_faces(
            Image={"Bytes": selfie_bytes},
            Attributes=["ALL"],  # include all face attributes for full liveness analysis
        )

        face_details = response.get("FaceDetails", [])

        if not face_details:
            logger.warning(f"No face detected in selfie: {selfie_image_key}")
            return LivenessResult(
                confidence=0.0,
                is_live=False,
                face_detected=False,
                error="No face detected in selfie image",
            )

        # Use the most prominent face (highest confidence detection)
        face = max(face_details, key=lambda f: f.get("Confidence", 0))

        # Calculate liveness score from multiple signals
        liveness_score = _calculate_liveness_score(face)

        is_live = liveness_score >= settings.LIVENESS_THRESHOLD

        logger.info(
            f"Liveness check complete — score: {liveness_score:.1f} "
            f"| is_live: {is_live}"
        )

        return LivenessResult(
            confidence=round(liveness_score, 2),
            is_live=is_live,
            face_detected=True,
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"Rekognition DetectFaces failed: {error_code} — {str(e)}")

        return LivenessResult(
            confidence=0.0,
            is_live=False,
            face_detected=False,
            error=f"AWS error during liveness check: {error_code}",
        )


def _calculate_liveness_score(face: dict) -> float:
    """
    Calculates a composite liveness score from multiple Rekognition
    face attribute signals.

    Signals and their weights:
    - Face detection confidence (how sure Rekognition is it's a face): 25%
    - Eyes open probability (closed eyes suggest a photo): 25%
    - Image sharpness (blurry = likely printed photo): 20%
    - Image brightness (too dark/bright = abnormal): 15%
    - Pose (facing camera directly): 15%

    Each signal is normalized to 0-100 before weighting.
    """
    # ── Signal 1: Face detection confidence (25%)
    face_confidence = face.get("Confidence", 0)

    # ── Signal 2: Eyes open probability (25%)
    # Average of left and right eye open confidence
    left_eye_open = face.get("EyesOpen", {}).get("Confidence", 50)
    right_eye_open = face.get("EyesOpen", {}).get("Value", False)
    # If eyes are detected as closed, penalize heavily
    eyes_score = left_eye_open if right_eye_open else (left_eye_open * 0.3)

    # ── Signal 3: Image sharpness (20%)
    quality = face.get("Quality", {})
    sharpness = quality.get("Sharpness", 50)  # 0-100

    # ── Signal 4: Image brightness (15%)
    # Ideal brightness is in the middle range — too dark or too bright = suspicious
    brightness = quality.get("Brightness", 50)
    # Penalize extreme brightness values
    brightness_score = 100 - (abs(brightness - 50) * 1.5)
    brightness_score = max(0, min(100, brightness_score))

    # ── Signal 5: Face pose — is person looking at camera (15%)
    pose = face.get("Pose", {})
    yaw = abs(pose.get("Yaw", 0))    # left/right rotation
    pitch = abs(pose.get("Pitch", 0)) # up/down rotation
    roll = abs(pose.get("Roll", 0))  # tilt
    # Penalize large pose deviations — looking away from camera
    pose_score = max(0, 100 - (yaw * 1.2) - (pitch * 1.2) - (roll * 0.5))

    # ── Weighted composite
    composite = (
        (face_confidence * 0.25) +
        (eyes_score * 0.25) +
        (sharpness * 0.20) +
        (brightness_score * 0.15) +
        (pose_score * 0.15)
    )

    return round(min(100.0, max(0.0, composite)), 2)