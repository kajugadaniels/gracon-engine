# Git Rules

Purpose: keep engine commits reviewable and copy-paste safe.

Codex must never run git commands automatically. Present commands only.

## Required Format

Paths are relative to `engine/`, where this service `requirements.txt` lives.

```bash
git add "app/services/scoring.py"
git commit -m "fix(engine): adjust composite score threshold handling"
```

## Rules

- One file per `git add`.
- Always quote paths.
- Never use `git add .` or `git add -A`.
- Never include `cd engine`.
- Never run `git push`.
- Use Conventional Commits.

## Common Scopes

- `engine` - verification service behavior.
- `verification` - verification job flow and scoring.
- `security` - API-key checks, docs disabling, privacy hardening.
- `rekognition` - AWS Rekognition wrappers.
- `config` - settings and environment behavior.
- `docs` - README and agent docs.
- `test` - test-only changes.
