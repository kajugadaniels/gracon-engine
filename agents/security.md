# Security Rules

Purpose: protect biometric inputs, internal API keys, AWS credentials, and verification decisions.

## Internal Boundary

- This service is internal-only. Do not add public-facing behavior.
- Only `api/auth` should call the engine.
- Do not issue, refresh, or validate user JWTs here.
- Do not add browser-specific CORS allowances unless the architecture is explicitly redesigned.

## API Key Validation

- Keep API-key validation constant-time with `hmac.compare_digest`.
- Do not log the configured API key or the presented API key.
- Return generic unauthorized errors.
- Keep API-key configuration required in production.

## Biometric Privacy

- Never persist ID-card, selfie, face crop, or biometric images to disk.
- Process S3 objects in memory only.
- Never log image bytes, extracted face metadata, raw Rekognition face details, S3 object bodies, or sensitive identity values.
- Treat every new log line as a production privacy decision.

## AWS And S3

- Do not expose AWS credentials, bucket names, object keys, or provider stack traces to clients.
- Validate S3 keys before retrieval when key constraints are available.
- Keep AWS clients inside service wrappers, not route handlers.

## Failure Behavior

- Avoid leaking whether a specific image, key, or provider resource exists.
- Convert provider failures into safe error responses for `api/auth`.
- Preserve enough internal logging for operations without exposing biometric details.
