# ---------------------------------------------------------------------------
# TotemEngine — Docker image
#
# Uses a slim Python base, installs Playwright + Chromium.
# No browsers needed on the host — everything runs in the container.
#
# Build:
#   docker build -t totemengine .
#
# CLI:
#   docker run --rm -e MISTRAL_API_KEY=xxx totemengine research "your query"
#
# Server:
#   docker run --rm -p 8000:8000 -e MISTRAL_API_KEY=xxx totemengine server
# ---------------------------------------------------------------------------

FROM python:3.12-slim

WORKDIR /app

# Install system deps required by Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency specs first (for Docker layer caching)
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy the rest of the application
COPY . .

# Install Playwright browsers (Chromium)
RUN python -m playwright install chromium

# Default command (shows help)
ENTRYPOINT ["python", "main.py"]
