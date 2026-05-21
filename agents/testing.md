# Testing Rules

Purpose: make verification scoring, security, and provider-error handling hard to regress.

## Commands

```bash
python -m pytest
python -m pytest tests
python -m compileall app main.py
```

Use the smallest command that proves the change. For docs-only changes, no runtime test is required.

## Test Placement

- Put tests under `tests/` when test infrastructure exists.
- Use focused unit tests for scoring and security helpers.
- Use route tests for authentication, validation, and safe error responses.
- Mock AWS Rekognition and S3; never call real AWS in unit tests.

## Priority Areas

1. Constant-time API-key validation behavior.
2. Production docs disabling.
3. Request validation for missing or malformed S3 keys.
4. Scoring thresholds and composite pass/fail decisions.
5. Missing-face, low-similarity, and low-liveness outcomes.
6. Safe provider-error mapping.
7. In-memory-only behavior for image processing.

## Test Data Rules

- Do not commit real ID-card or face images.
- Use tiny synthetic fixtures or fully mocked byte streams.
- Do not include real NID/PID, S3 keys, or AWS response data in fixtures.
