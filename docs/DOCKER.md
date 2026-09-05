# Docker & Render Deployment

WebHunter runs entirely inside Docker. You do **not** need Python, Playwright, or Chromium installed on the host machine — everything is packaged into a single container image.

> **Docker-first deployment.** This guide covers local Docker, plain `docker run`, and Render.

---

## Prerequisites

- **Docker Engine** 24.0+ or **Docker Desktop** with Compose plugin

> No Python runtime, virtual environment, or browser required on the host.

---

## Local: Quick Start

### 1. Clone

```bash
git clone https://github.com/nayaksomkar/WebHunter.git
cd WebHunter
```

### 2. (Optional) Configure environment

```bash
cp .env.example .env
nano .env   # adjust PORT, MAX_PAGES, etc. if needed
```

Defaults work for most cases.

### 3. Build

```bash
docker compose build
```

This runs:
1. `pip install -e .` — installs all Python dependencies
2. `python -m playwright install chromium` — downloads the Chromium binary into the image

### 4. Run

```bash
docker compose up server
```

The server listens on `http://localhost:8000` (or whatever `$PORT` is).

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

---

## Plain Docker (without Compose)

```bash
# Build
docker build -t webhunter .

# Run
docker run --rm -p 8000:8000 -e PORT=8000 webhunter
```

---

## Docker Compose Reference

Defined in [`docker-compose.yml`](../docker-compose.yml):

| Service | Purpose | Ports | Image |
|---------|---------|-------|-------|
| `server` | FastAPI REST API server | `${PORT:-8000}:${PORT:-8000}` | `webhunter` |

The service honors every environment variable from [`.env.example`](../.env.example).

---

## Render Deployment

Render is the recommended host for this service.

### One-time setup

1. Push this repository to GitHub or GitLab.
2. On Render, click **New → Web Service**.
3. Select the repo. Render auto-detects the `Dockerfile` — no build command override needed.
4. Configure:
   - **Environment:** `Docker`
   - **Region:** pick one close to your other microservices
   - **Instance Type:** `Starter` or higher (Chromium needs ~512MB RAM minimum)
   - **Health Check Path:** `/health`
5. No environment variables are required. Add them only if you want to override defaults.

### What happens on deploy

- Render sets `$PORT` automatically (usually `10000`).
- WebHunter reads it via `totem.config.PORT` and binds Uvicorn accordingly.
- Health checks pass once `GET /health` returns `{"status":"ok"}`.
- First deploy takes **2–3 minutes** (Chromium download + install). Subsequent deploys reuse cached layers and are typically <30s.

### Verifying a Render deployment

```bash
curl https://<your-service>.onrender.com/health
# → {"status":"ok"}

curl -X POST https://<your-service>.onrender.com/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query":"EV market 2025","max_pages":2,"variants":["pricing"]}'
```

---

## What's Inside the Image

The [`Dockerfile`](../Dockerfile) builds a self-contained image:

| Layer | Details |
|-------|---------|
| Base | `python:3.12-slim` |
| System deps | `wget`, `ca-certificates` (required by Chromium) |
| Python deps | `pip install -e .` → installs `fastapi`, `uvicorn`, `pydantic`, `ddgs`, `playwright`, `python-dotenv` |
| Browser | `playwright install chromium` → Chromium binary baked into the image |
| Entrypoint | `CMD ["server"]` — Uvicorn runs on `0.0.0.0:$PORT` |

**What you do NOT need on the host:**

- Python / pip / venv
- Playwright browsers
- Chromium or any GUI libraries
- Any Node.js or frontend tooling
- Any API keys (there are none — WebHunter has no LLM provider)

---

## Environment Variables

All configuration is via environment variables. Docker Compose reads them from `.env`.

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server bind port (Render sets automatically) |
| `HOST` | `0.0.0.0` | Server bind host |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_RESULTS` | `6` | Max URLs collected per research request |
| `MAX_PAGES` | `3` | Max pages crawled per research request |
| `PAGE_TIMEOUT_MS` | `30000` | Per-page Playwright navigation timeout |
| `CONTENT_MAX_CHARS` | `8000` | Cap on extracted text per page |
| `SEARCH_VARIANTS` | _empty_ | Comma-separated extra query suffixes applied to every request |

See [CONFIGURATION.md](CONFIGURATION.md) for the full reference.

---

## Troubleshooting

### Build fails during `playwright install chromium`

The step downloads ~300MB. Ensure:
- Sufficient disk space (500MB+ free on the build machine)
- Network access to `playwright.azureedge.net`

### Container exits immediately

Check logs:
```bash
docker compose logs server
```

Common causes:
- Port collision (change `PORT` in `.env`)
- Missing `CMD` argument (ensure your image inherits `CMD ["server"]` from the Dockerfile)

### API returns 500

Check container logs:
```bash
docker compose logs -f server
```

Possible causes:
- DuckDuckGo rate-limit (will be visible as `Search failed for '...'` warnings; pipeline continues)
- All crawl targets unreachable from the container's network

### Playwright fails to launch Chromium

If you see `BrowserType.launch: Executable doesn't exist`, the image wasn't built with `playwright install chromium`. Rebuild:
```bash
docker compose build --no-cache
```

---

## Related

- [README.md](../README.md) — Project overview
- [API.md](API.md) — REST API reference
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables
- [ARCHITECTURE.md](ARCHITECTURE.md) — Internals
