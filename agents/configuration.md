# Configuration Rules

Purpose: keep engine behavior environment-driven and production-safe.

## Environment Variables

- Add every new variable to `.env.example`.
- Never commit real `.env` or `.env.production` values.
- Use Pydantic settings in `app/core/config.py`; do not read `os.environ` throughout the codebase.
- Keep threshold values configurable instead of hardcoding them inside route handlers or services.

## Required Configuration Areas

- App environment and port.
- Internal engine API key.
- AWS region and credentials.
- S3 bucket name.
- Face similarity threshold.
- Liveness threshold.
- Composite pass threshold.

## Threshold Rules

- Threshold defaults must be conservative.
- If threshold semantics change, update `README.md`, `.env.example`, tests, and scoring documentation.
- A threshold of zero should only be allowed if the business and security meaning is explicitly documented.

## Production Rules

- Production must require API-key configuration.
- Production must disable public FastAPI docs.
- Provider errors must not reveal configuration internals to callers.
