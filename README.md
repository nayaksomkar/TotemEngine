<div align="center">

# WebHunter

**Standalone web search + crawling microservice** — DuckDuckGo for discovery, Playwright for page content.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.137%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/playwright-%E2%80%93-2e8533?logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker](https://img.shields.io/badge/docker-%E2%80%93-2496ED?logo=docker&logoColor=white)](https://docker.com)

**One container** · **REST API** · **No LLM** · **No database** · **Render-ready**

</div>

---

## What It Does

WebHunter is a focused microservice that:

1. Takes a single research query (plus optional variant suffixes) over HTTP
2. Runs DuckDuckGo text search across the query and its variants
3. Crawls the top URLs with headless Chromium (Playwright) — handles JS-heavy sites
4. Returns a structured JSON payload with every URL found, every page fetched, and the cleaned text content of each page

That's it. WebHunter knows nothing about LLMs, providers, or orchestration — those responsibilities live in **CompetitorEngine** (orchestrator) and **LLMPing** (LLM provider).

```
                ┌─────────────────────┐
                │ CompetitorEngine    │   (orchestrator)
                └──────────┬──────────┘
                           │ HTTP /research/sync
                           ▼
                ┌─────────────────────┐
                │     WebHunter       │   ← this service
                │   (search + crawl)  │
                └──────────┬──────────┘
                           │ HTTP /chat
                           ▼
                ┌─────────────────────┐
                │      LLMPing        │   (AI / LLM provider)
                └─────────────────────┘
```

**LLMPing** handles all AI / ML tasks — query decomposition, per-page summarization, and final synthesis — over its `/chat` endpoint. WebHunter does not talk to it directly; CompetitorEngine orchestrates the call.

- **LLMPing repo:** [https://github.com/nayaksomkar/LLMPing](https://github.com/nayaksomkar/LLMPing)
- **LLMPing deployed:** `https://llmping.onrender.com`
- **WebHunter deployed:** `https://webhunter.onrender.com`
- **Local dev:** `http://localhost:8000` (this service), `http://localhost:<llmping-port>` for LLMPing when running both locally

---

## Quick Start

### Prerequisites

- **Docker** (Engine 24.0+ or Docker Desktop with Compose plugin)

> No Python runtime, Playwright browsers, or Chromium on the host — everything ships inside the image.

### 1. Clone

```bash
git clone https://github.com/nayaksomkar/WebHunter.git
cd WebHunter
```

### 2. Configure (optional — sensible defaults work)

```bash
cp .env.example .env
```

The defaults (`PORT=8000`, `MAX_RESULTS=6`, `MAX_PAGES=3`, `PAGE_TIMEOUT_MS=30000`) are picked for typical competitive-research queries. Override anything you need.

### 3. Build

```bash
docker compose build
```

This installs Python deps and pre-bakes Chromium (~300MB) into the image.

### 4. Run

```bash
docker compose up server
```

Health check:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

---

## Sample Request / Response

### `POST /research/sync`

**Request:**

```bash
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{
    "query": "electric vehicle market leaders 2025",
    "max_pages": 3,
    "variants": ["pricing", "competitors"]
  }'
```

**Response (200):**

```json
{
  "status": "completed",
  "query": "electric vehicle market leaders 2025",
  "search_queries": [
    "electric vehicle market leaders 2025",
    "electric vehicle market leaders 2025 pricing",
    "electric vehicle market leaders 2025 competitors"
  ],
  "search_results": [
    {
      "sub_query": "electric vehicle market leaders 2025 pricing",
      "url": "https://www.statista.com/...",
      "title": "Top 10 EV makers by market share — Statista",
      "snippet": "Tesla led the global EV market in Q1 2025..."
    }
  ],
  "crawled_contents": [
    {
      "url": "https://www.statista.com/...",
      "sub_query": "electric vehicle market leaders 2025 pricing",
      "title": "Top 10 EV makers by market share",
      "content": "...plain text, up to CONTENT_MAX_CHARS..."
    }
  ],
  "stats": {
    "search_results_count": 7,
    "crawled_pages_count": 3,
    "elapsed_ms": 48211
  },
  "errors": []
}
```

See [docs/API.md](docs/API.md) for the complete contract and error shapes.

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health check (Render pings this) |
| `POST` | `/research/sync` | Run search + crawl synchronously (blocks 15–90s) |
| `POST` | `/research` | Start async research; returns `task_id` |
| `GET` | `/research/{task_id}` | Poll async task result |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `8000` | Server bind port. Render sets this automatically. |
| `HOST` | No | `0.0.0.0` | Server bind host. |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_RESULTS` | No | `6` | Max URLs collected across all search queries. |
| `MAX_PAGES` | No | `3` | Max pages actually crawled per request. |
| `PAGE_TIMEOUT_MS` | No | `30000` | Per-page Playwright navigation timeout. |
| `CONTENT_MAX_CHARS` | No | `8000` | Cap on extracted text per page. |
| `SEARCH_VARIANTS` | No | _empty_ | Comma-separated extra query suffixes applied to every request unless overridden by the caller's `variants` field. |

> **No LLM keys needed.** WebHunter never talks to an LLM directly.

---

## Deployment

### Local Docker

```bash
docker compose build
docker compose up server
# → listening on http://localhost:8000
```

### Plain Docker

```bash
docker build -t webhunter .
docker run --rm -p 8000:8000 -e PORT=8000 webhunter
```

### Render

1. Push this repo to GitHub/GitLab.
2. On Render, click **New → Web Service → Docker**.
3. Render auto-detects the `Dockerfile`. Override as needed:
   - **Health Check Path:** `/health`
   - **Port:** Render sets `$PORT` automatically; `webhunter` reads it.
   - **Environment:** none required (no API keys).
4. First deploy takes ~2–3 minutes (Chromium download). Subsequent deploys are fast thanks to layer caching.

After deploy:

```bash
curl https://<your-service>.onrender.com/health
# → {"status":"ok"}
```

### Calling WebHunter From Another Microservice

```python
import httpx

resp = httpx.post(
    "https://<your-service>.onrender.com/research/sync",
    json={
        "query": "lithium-ion battery manufacturers",
        "max_pages": 3,
        "variants": ["pricing", "market share"],
    },
    timeout=180.0,
)
data = resp.json()
for page in data["crawled_contents"]:
    print(page["url"], page["content"][:200])
```

The caller (e.g. CompetitorEngine) decides what to do with the returned text — summarize via LLMPing, embed, store, etc.

---

## What's Inside the Image

Base `python:3.12-slim` plus:

| Layer | Details |
|-------|---------|
| System deps | `wget`, `ca-certificates` (required by Chromium) |
| Python deps | `fastapi`, `uvicorn`, `pydantic`, `ddgs`, `playwright`, `python-dotenv` |
| Browser | Chromium pre-installed via `playwright install chromium` |
| Entrypoint | `python main.py server` |

No LangChain, no LangGraph, no model provider SDKs, no databases, no Redis — by design.

---

## Documentation

| File | Description |
|------|-------------|
| [docs/API.md](docs/API.md) | Full REST API reference with request/response examples |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline internals, data flow, file tree |
| [docs/DOCKER.md](docs/DOCKER.md) | Docker & Render deployment guide |
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Environment variables reference |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Local (non-Docker) development setup |

---

## Out of Scope

WebHunter deliberately does **not**:

- Call any LLM (no Mistral, no Groq, no ChatCompletion APIs)
- Store data between requests (no DB, no Redis)
- Orchestrate multi-service workflows (that's CompetitorEngine)
- Authenticate callers (assumed private network; add `Authorization` if exposing publicly)

---

<div align="center">
  <sub>
    Built with FastAPI, DuckDuckGo, and Playwright.
    ·
    <a href="https://github.com/nayaksomkar/WebHunter">GitHub</a>
  </sub>
</div>
