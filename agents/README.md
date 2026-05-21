# Engine Agent Guide

Purpose: this directory gives AI agents project-local rules for working on the Gracon internal verification engine without weakening biometric privacy, internal-service authentication, AWS Rekognition behavior, or scoring integrity.

Read this file first, then read the topic file that matches the change.

## Reading Order

1. `folder-structure.md` - where new code belongs.
2. `file-structure.md` - Python naming, typing, comments, and exported API expectations.
3. `security.md` - internal-only boundary, API-key checks, biometric privacy, and logging rules.
4. `api-contracts.md` - FastAPI route, Pydantic model, and response-contract rules.
5. `configuration.md` - environment variable and threshold configuration rules.
6. `verification-engine.md` - verification job, S3, Rekognition, and scoring rules.
7. `testing.md` - required test shape and areas to cover.
8. `documentation.md` - when README and `.env.example` must change.
9. `git.md` - copy-paste commit format for this service.

## Service Boundary

`engine` is an internal FastAPI service called by `api/auth`. It validates verification-job requests, downloads temporary S3 assets in memory, calls AWS Rekognition, computes final pass/fail decisions, and returns structured results.

It must never be exposed publicly, issue tokens, persist biometric images, or own user-account verification state. `api/auth` owns user verification workflow state and database writes.

## Conflict Rule

If a local rule here conflicts with root `AGENTS.md`, follow the stricter security or privacy rule and update documentation after the decision is made.
