# Contributing

Development setup is **optional** — WebHunter is designed to run entirely inside Docker.  
This guide is for contributors who want to edit the code and test locally without rebuilding the image every time.

> For end-user Docker deployment, see [DOCKER.md](DOCKER.md).

---

## Development Prerequisites

- **Python 3.12+**
- **Playwright** CLI (`pip install playwright`)
- **Chromium** browser (`playwright install chromium`)

> **No API keys needed.** WebHunter has no LLM provider integration.

---

## Local Setup

### 1. Clone

```bash
git clone https://github.com/nayaksomkar/WebHunter.git
cd WebHunter
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -e .
playwright install chromium
```

### 4. Configure environment (optional)

Defaults are sensible — only override if you need to:

```bash
cp .env.example .env
nano .env
```

### 5. Run

```bash
python main.py server --port 8000
curl http://localhost:8000/health
```

---

## Project Structure

```
webhunter/
├── main.py              # Entrypoint
├── Dockerfile           # Container image
├── docker-compose.yml   # Local stack
├── docs/                # Documentation
├── totem/
│   ├── cli.py           # CLI parser (only `server`)
│   ├── server.py        # FastAPI HTTP layer
│   ├── pipeline.py      # Search + crawl orchestrator
│   ├── search_client.py # ddgs wrapper + query expansion
│   ├── crawl_client.py  # Playwright scraper
│   ├── config.py        # Env-driven config (no API keys)
│   └── models.py        # TypedDicts (SearchResult, ResearchResult, ...)
└── tests/               # Tests (if added)
```

---

## Code Style

- Python, 4-space indentation
- Type hints preferred
- No external comments unless explaining non-obvious logic
- Follow existing patterns in `totem/`

---

## Testing

No automated tests yet. To verify changes manually:

```bash
# Server
python main.py server --port 8000

# Health
curl http://localhost:8000/health

# Sync research
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "max_pages": 1}'

# Direct Python invocation of the pipeline
python -c "from totem.pipeline import run_research; import json; print(json.dumps(run_research('test query', {'max_pages':1}), indent=2, default=str))"
```

---

## Docker Workflow for Contributors

Rebuild after code changes:

```bash
docker compose build
docker compose up server
```

Force rebuild (no cache):

```bash
docker compose build --no-cache
```

---

## Adding a New Search Provider

1. Implement a function in `totem/search_client.py` that returns `list[SearchResult]` (same TypedDict shape as `ddgs` results).
2. Add a `provider` field to `ResearchRequest` and dispatch inside `pipeline.run_research()`.
3. Update `.env.example` and [CONFIGURATION.md](CONFIGURATION.md) if the provider needs new env vars.

---

## Related

- [DOCKER.md](DOCKER.md) — Docker & Render deployment
- [ARCHITECTURE.md](ARCHITECTURE.md) — Pipeline internals
- [API.md](API.md) — REST API reference
