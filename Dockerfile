# ─── Production Stage ─────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Run as non-root for security
RUN useradd -m -u 1001 appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use uvicorn directly (not the __main__ block which is for local dev)
# Workers=2 is a safe default; tune based on available CPU cores
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
