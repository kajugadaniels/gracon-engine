# API Contract Rules

Purpose: keep FastAPI routes stable for `api/auth` and safe for internal verification jobs.

## Route Rules

- All routes must live under the versioned API router.
- Verification routes must require internal API-key authentication.
- Route handlers should be async only when the underlying operations benefit from it.
- Do not return raw AWS Rekognition responses.

## Pydantic Rules

- Request and response schemas belong in `app/models/`.
- Use strict field names that match `api/auth` integration contracts.
- Include validation constraints for required S3 keys, IDs, thresholds, and optional metadata.
- Keep response models explicit for pass/fail decision, score details, and safe failure reasons.

## Error Contract

- Return safe, generic client-facing errors.
- Include detailed provider context only in sanitized internal logs.
- Keep error shapes stable so `api/auth` can map failures consistently.

## Docs Behavior

- OpenAPI docs may be enabled in development.
- `/docs` and `/redoc` must stay disabled in production.
- Do not document or expose secrets in examples.
