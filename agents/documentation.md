# Documentation Rules

Purpose: keep internal verification-engine behavior understandable and safe to operate.

## Update Documentation When

- Verification request or response models change.
- API-key, docs disabling, or internal-service security behavior changes.
- AWS Rekognition integration behavior changes.
- Thresholds, scoring math, or pass/fail semantics change.
- New environment variables are added.
- Error behavior changes in a way `api/auth` must handle.

## Required Places

- `engine/README.md` for service-local architecture and commands.
- `engine/.env.example` for new configuration.
- `api/auth/README.md` if `api/auth` integration behavior changes.
- Root `AGENTS.md` only when the cross-project platform picture changes.

## Documentation Quality

- Explain privacy constraints clearly.
- State whether behavior is development-only or production-required.
- Avoid example secrets, real S3 keys, real biometric data, or realistic identity values.
