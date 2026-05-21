# File Structure Rules

Purpose: keep Python engine files typed, readable, and privacy-safe.

## Required File Shape

- Every file must start with a short module docstring explaining its purpose.
- Every public function, class, and method must have a docstring explaining what it does, parameters, and return value.
- Use Python type hints for function inputs and returns.
- Avoid untyped dictionaries for structured data; use Pydantic models or typed helpers.
- Delete dead code instead of commenting it out.

## Naming

- Files: `snake_case.py`
- Functions and variables: `snake_case`
- Classes and Pydantic models: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: prefix with `_` only when they are intentionally module-local.

## Comments

- Explain privacy and security decisions directly.
- Add comments before threshold calculations or scoring rules that would be easy to misread.
- Never add comments containing real S3 keys, API keys, NID/PID values, or biometric metadata.

## Route Handler Shape

- Validate input with Pydantic models.
- Authenticate the internal caller before expensive work.
- Keep route handlers orchestration-focused.
- Return response models, not raw AWS responses.
- Convert provider errors into safe internal error responses.
