# Folder Structure Rules

Purpose: define where engine code belongs so verification, security, Rekognition, and scoring responsibilities stay separated.

## Current Layout

```text
engine/
  agents/              AI-agent project rules
  app/
    api/
      router.py        top-level API router composition
      v1/
        health.py      internal health endpoints
        verification.py verification job endpoint
    core/
      config.py        Pydantic settings and environment parsing
      logging.py       privacy-aware logging setup
      security.py      internal API-key validation
    exceptions/
      handlers.py      safe exception responses
    models/
      requests.py      Pydantic request schemas
      responses.py     Pydantic response schemas
    services/
      rekognition/     AWS Rekognition client and operation wrappers
      scoring.py       final verification score calculation
  main.py              FastAPI app factory and startup wiring
  requirements.txt     Python dependencies
```

## Placement Rules

- Put HTTP routes under `app/api/v1/`.
- Put Pydantic schemas under `app/models/`.
- Put settings and security primitives under `app/core/`.
- Put AWS Rekognition integration code under `app/services/rekognition/`.
- Put final pass/fail math in `app/services/scoring.py` or a focused scoring helper.
- Put exception normalization in `app/exceptions/`.

## New File Rules

- Add new folders only when they represent a durable boundary.
- Do not put AWS client code inside route handlers.
- Do not put request validation inside Rekognition wrappers when Pydantic can validate at the route edge.
- Keep `main.py` focused on app construction and middleware/router wiring.
