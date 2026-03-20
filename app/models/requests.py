from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    """
    Request body sent by NestJS gateway to the engine.

    Images are NOT sent as raw bytes — the gateway uploads them to S3
    and passes the S3 object keys. The engine fetches them directly
    from S3 using its own AWS credentials.

    This approach:
    - Keeps image data off the network between services
    - Leverages IAM permissions — engine only needs S3 read access
    - Avoids multipart/form-data complexity between services
    """

    # S3 object keys — not full URLs, just the key within the bucket
    # Example: "verification-temp/abc123-id-card.jpg"
    id_image_key: str = Field(
        ...,
        description="S3 object key for the uploaded ID card image",
        min_length=1,
        max_length=512,
    )

    selfie_image_key: str = Field(
        ...,
        description="S3 object key for the uploaded selfie image",
        min_length=1,
        max_length=512,
    )

    # User context — for logging and audit only, not used in AI checks
    user_id: str = Field(
        ...,
        description="UUID of the user being verified — for audit logging",
        min_length=36,
        max_length=36,
    )