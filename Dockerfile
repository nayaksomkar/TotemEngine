# ---------------------------------------------------------------------------
# WebHunter — Docker image
#
# Self-contained: Python + Playwright + Chromium. No external services
# required. Designed to run on Render (CMD ["server"] lets Render control
# the entrypoint).
#
# Build:
#   docker build -t webhunter .
#
# Run locally:
#   docker run --rm -p 8000:8000 -e PORT=8000 webhunter
#
# Render:
#   PORT=10000 (set automatically), health check at GET /health
# ---------------------------------------------------------------------------

FROM python:3.12-slim

WORKDIR /app

# System deps required by Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Dependency specs first for layer caching
COPY pyproject.toml requirements.txt ./

RUN pip install --no-cache-dir -e .

# App source
COPY . .

# Pre-bake Chromium into the image (one-time ~300MB download)
RUN python -m playwright install chromium

# Expose the configured port (Render overrides with $PORT)
EXPOSE 8000

# Default command starts the server. Render's $PORT is honored by cli.py
# via totem.config.PORT.
CMD ["server"]
