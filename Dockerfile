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

# System deps required by Chromium (libglib, libnss, libnspr, libdbus, etc.)
# `playwright install-deps` installs exactly the libraries the bundled
# Chromium build needs, version-matched to the Python package.
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Dependency specs first for layer caching
COPY pyproject.toml requirements.txt ./

RUN pip install --no-cache-dir -e .

# App source
COPY . .

# Pre-bake Chromium + its system libraries into the image
RUN python -m playwright install --with-deps chromium

# Expose the configured port (Render overrides with $PORT)
EXPOSE 8000

# Default command starts the server. Render's $PORT is honored by cli.py
# via totem.config.PORT.
CMD ["python", "main.py", "server"]
