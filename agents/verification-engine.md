# Verification Engine Rules

Purpose: preserve the verification job flow from `api/auth` through S3, AWS Rekognition, scoring, and safe response generation.

## Ownership

- `api/auth` owns verification state, attempts, rate limits, users, and database records.
- `engine` owns only the internal verification computation for one request.
- Do not move user workflow state into this service.

## Verification Flow

1. Validate the request model.
2. Validate the internal API key.
3. Retrieve required S3 objects in memory.
4. Run face comparison and liveness checks through Rekognition wrappers.
5. Calculate final scores with the scoring service.
6. Return a safe structured result to `api/auth`.

## Rekognition Rules

- Keep AWS calls behind `app/services/rekognition/` wrappers.
- Normalize AWS responses before scoring.
- Do not expose provider-specific raw payloads in API responses.
- Handle missing faces, low-quality images, and provider errors explicitly.

## Scoring Rules

- Keep final decision logic in `app/services/scoring.py` or a focused helper.
- Use configured thresholds.
- Keep composite scoring deterministic and covered by tests.
- Return enough score detail for `api/auth` to explain a safe result without leaking biometric internals.

## Data Handling

- Images stay in memory and are discarded after the request.
- Never write request images or derived biometric artifacts to disk.
- Avoid adding caches for biometric data unless the architecture is explicitly reviewed.
