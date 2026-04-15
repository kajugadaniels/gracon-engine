# Engine

Internal AI verification engine for the Gracon platform.

This FastAPI service receives S3 keys for ID-card and selfie images from `api/auth`, downloads the assets in memory, calls AWS Rekognition, computes a structured verification result, and returns a pass/fail decision with supporting scores. It is an internal-only service and should never be exposed publicly.

## Overview

- Runtime: FastAPI + Python 3.11+
- Default port: `8000`
- AI provider: AWS Rekognition
- Primary caller: `api/auth`

## What This Service Owns

- Request validation for verification jobs
- Secure engine API-key validation
- In-memory S3 object retrieval
- Face-comparison and liveness calls to Rekognition
- Scoring and pass/fail calculation
- Clean JSON responses and exception handling

## Core Skills Needed

- FastAPI and Pydantic
- Secure internal-service authentication
- AWS Rekognition integration
- Defensive logging and exception handling
- In-memory file processing

## Techniques Used

- `hmac.compare_digest` for constant-time API-key checks
- Pydantic settings and request/response models
- In-memory processing only, no disk persistence for biometric images
- Environment-controlled thresholds for similarity/liveness/composite pass score
- Production docs disabling for `/docs` and `/redoc`

## Main Areas

```text
app/
  api/v1/          verification and health endpoints
  core/            config, logging, security
  exceptions/      global handlers
  models/          request and response schemas
  services/
    rekognition/   AWS client wrappers
    scoring.py     final decision logic
main.py            app factory and startup wiring
```

## Folder Structure

```text
engine/
  app/
  main.py
  requirements.txt
  .env.example
```

## Local Commands

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Notes

Key variables:

```env
APP_ENV=development
APP_PORT=8000
ENGINE_API_KEY=
AWS_REGION=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET_NAME=
FACE_SIMILARITY_THRESHOLD=70.0
LIVENESS_THRESHOLD=70.0
COMPOSITE_PASS_THRESHOLD=80.0
```

## Integration Boundaries

- Only `api/auth` should call this service
- Should not be internet-facing
- Must never persist images or emit biometric PII in logs

## Important Rules

- Keep API-key validation constant-time
- Never write image data to disk
- Disable public docs in production
- Keep thresholds in config, not hardcoded inside handlers

## Contribution Checklist

- Preserve internal-only assumptions
- Treat every new log line as a privacy decision
- Test error handling and production docs disabling when adding endpoints

