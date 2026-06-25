# Contributing

Development setup is **optional** — TotemEngine is designed to run entirely inside Docker.  
This guide is for contributors who want to edit the code and test locally without rebuilding the image every time.

> For end-user Docker deployment, see [DOCKER.md](DOCKER.md).

---

## Development Prerequisites

- **Python 3.12+**
- **Playwright** CLI (`pip install playwright`)
- **Chromium** browser (`playwright install chromium`)
- API key from [Mistral AI](https://console.mistral.ai/) or [Groq](https://console.groq.com/)

---

## Local Setup

### 1. Clone

```bash
git clone https://github.com/nayaksomkar/TotemEngine.git
cd TotemEngine
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

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Run

```bash
python main.py research "How does quantum computing work?" --model mistral
python main.py server --port 8000
```

---

## Project Structure

```
totemengine/
├── main.py              # Entrypoint
├── Dockerfile           # Container image
├── docker-compose.yml   # Compose stacks
├── docs/                # Documentation
├── totem/
│   ├── cli.py           # CLI parser
│   ├── server.py        # FastAPI server
│   ├── graph.py         # LangGraph workflow
│   ├── nodes.py         # Pipeline stages
│   ├── crawl_client.py  # Playwright scraper
│   ├── llm.py           # LLM factory
│   ├── config.py        # Env vars + model config
│   └── models.py        # Shared types
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

No automated tests yet. To verify changes:

```bash
# CLI
python main.py research "test query" --model mistral

# Server
python main.py server --port 8000
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "model": "mistral"}'
```

---

## Docker Workflow for Contributors

Rebuild after code changes:

```bash
docker compose build
docker compose run --rm cli research "test query"
docker compose up server
```

Force rebuild (no cache):

```bash
docker compose build --no-cache
```

---

## Adding a New Model

1. Define the provider client in [`totem/llm.py`](../totem/llm.py)
2. Add an entry to `SUPPORTED_MODELS` in [`totem/config.py`](../totem/config.py)
3. Update `.env.example` with the new API key field
4. Document in [CONFIGURATION.md](CONFIGURATION.md)

---

## Related

- [DOCKER.md](DOCKER.md) — Docker deployment
- [ARCHITECTURE.md](ARCHITECTURE.md) — Pipeline internals
- [API.md](API.md) — REST API reference
