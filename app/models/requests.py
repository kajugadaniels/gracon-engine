from pydantic import BaseModel, Field # type: ignore


class VerificationRequest(BaseModel):
    id_image_key: str = Field(..., min_length=1, max_length=512)
    selfie_image_key: str = Field(..., min_length=1, max_length=512)
    user_id: str = Field(..., min_length=36, max_length=36)

    # Document match result from NestJS gateway
    # Gateway decrypts stored NID and compares with user input
    # Engine trusts this value — gateway is responsible for the check
    document_match: bool = Field(
        ...,
        description="Whether the user's typed NID matched their stored encrypted NID",
    )