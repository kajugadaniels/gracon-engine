from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import get_settings

# Header name the NestJS gateway must send on every request
# Example: X-Engine-API-Key: your_secret_key
API_KEY_HEADER = APIKeyHeader(name="X-Engine-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    FastAPI dependency — validates the internal API key on every request.

    This engine is INTERNAL — it should never be reachable from the internet.
    The API key is a second layer of defence in case network rules are misconfigured.

    Usage: add `api_key: str = Depends(verify_api_key)` to any endpoint.
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-Engine-API-Key header.",
        )

    # Constant-time comparison — prevents timing attacks
    # An attacker measuring response time cannot guess the key character by character
    import hmac
    is_valid = hmac.compare_digest(
        api_key.encode("utf-8"),
        settings.ENGINE_API_KEY.encode("utf-8"),
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )

    return api_key