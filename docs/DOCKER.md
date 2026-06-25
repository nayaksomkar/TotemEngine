# Docker Deployment Guide

## Overview

TotemEngine runs entirely inside Docker. You do **not** need Python, Playwright, or Chromium installed on your host machine — everything is packaged into a single container image.

> **Docker-only deployment.** This guide covers running the project exclusively via Docker.  
> For local (non-Docker) development, see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Prerequisites

- **Docker Engine** 24.0+ or **Docker Desktop**
- **Docker Compose** plugin (included with Docker Desktop)
- API key from [Mistral AI](https://console.mistral.ai/) or [Groq](https://console.groq.com/)

> No Python runtime, virtual environment, or browser required on the host.

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/nayaksomkar/TotemEngine.git
cd TotemEngine
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add at least one API key:

```bash
MISTRAL_API_KEY=your-mistral-key-here
GROQ_API_KEY=your-groq-key-here
LOG_LEVEL=INFO
```

> **Where to change `.env`** — the file lives at the project root. Docker Compose reads it automatically.  
> **What to change** — at least one of `MISTRAL_API_KEY` or `GROQ_API_KEY`.

### 3. Build the image

```bash
docker compose build
```

This runs:
1. `pip install --no-cache-dir -e .` — installs all Python dependencies
2. `python -m playwright install chromium` — downloads the Chromium binary into the image

### 4. Run

**One-shot CLI query:**

```bash
docker compose run --rm cli research "How does quantum computing work?" --model mistral
```

**Start the API server:**

```bash
docker compose up server
```

---

## Docker Compose Services

Defined in [`docker-compose.yml`](../docker-compose.yml):

| Service | Purpose | Ports | Image |
|---------|---------|-------|-------|
| `totem` | Research CLI — runs one-off queries | none | `totemengine` |
| `server` | FastAPI REST API server | `8000:8000` | `totemengine` |

Both services share the same built image (`totemengine`).

---

## CLI Reference (Docker)

Run via the `cli` service:

```bash
# Research a query
docker compose run --rm cli research "your query" --model mistral

# List available models
docker compose run --rm cli models

# Start server (use 'up' instead of 'run')
docker compose up server
```

| Flag | Default | Description |
|------|---------|-------------|
| `--model` / `-m` | `mistral` | AI provider: `mistral` or `groq` |

---

## REST API Reference (Docker)

Start the server:

```bash
docker compose up server
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/models` | List available models |
| `POST` | `/research` | Start async research (returns `task_id`) |
| `GET` | `/research/{task_id}` | Poll async result |
| `POST` | `/research/sync` | Run research synchronously (blocks) |

### Example: Sync research

```bash
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question", "model": "mistral"}'
```

### Example: Async research

```bash
# Start task
TASK=$(curl -s -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question"}' | jq -r .task_id)

# Poll for result
curl http://localhost:8000/research/$TASK
```

---

## What's Inside the Image

The Dockerfile [`Dockerfile`](../Dockerfile) builds a self-contained image:

| Layer | Details |
|-------|---------|
| Base | `python:3.12-slim` |
| System deps | `wget`, `ca-certificates` (required by Chromium) |
| Python deps | `pip install -e .` → installs `totem`, `playwright`, `langchain`, `fastapi`, etc. |
| Browser | `playwright install chromium` → Chromium binary baked into the image |
| Entrypoint | `python main.py` |

**What you do NOT need on the host:**

- Python / pip / venv
- Playwright browsers
- Chromium or any GUI libraries
- Any Node.js or frontend tooling

---

## Environment Variables

All configuration is via environment variables. Docker Compose reads them from `.env`.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | For `mistral` model | — | Mistral AI API key |
| `GROQ_API_KEY` | For `groq` model | — | Groq API key |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`) |

See [CONFIGURATION.md](CONFIGURATION.md) for details.

---

## Troubleshooting

### Build fails with playwright install errors

The `playwright install chromium` step downloads ~300MB. Ensure:
- Sufficient disk space (500MB+ free)
- Network access to `playwright.azureedge.net`

### Container exits immediately

Check logs:
```bash
docker compose run --rm cli research "test" --model mistral
```

For server:
```bash
docker compose up server
```

### API returns 500

Verify your API key is set in `.env` and the container was rebuilt after changes:

```bash
docker compose build
docker compose up server
```

### Port 8000 already in use

Change the port mapping in `docker-compose.yml`:
```yaml
services:
  server:
    ports:
      - "9000:8000"   # map host:container
```

---

## Advanced: Build Only (No Compose)

```bash
# Build image manually
docker build -t totemengine .

# Run CLI query
docker run --rm -e MISTRAL_API_KEY=xxx totemengine research "query"

# Run server on port 8000
docker run --rm -p 8000:8000 -e MISTRAL_API_KEY=xxx totemengine server
```

---

## Related

- [README.md](../README.md) — Project overview and features
- [CONFIGURATION.md](CONFIGURATION.md) — Detailed environment setup
- [ARCHITECTURE.md](ARCHITECTURE.md) — Pipeline internals
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Local development setup
