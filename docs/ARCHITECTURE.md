# Architecture

TotemEngine is a multi-stage AI research pipeline built on LangGraph. Each stage is a node in a directed graph that passes structured data to the next stage.

## Pipeline Overview

```
User Query
    │
    ▼  DECOMPOSE  (LLM)
    │  Breaks query into 3-5 sub-queries
    │
    ▼  SEARCH  (DuckDuckGo)
    │  Returns URLs for each sub-query
    │
    ▼  CRAWL  (Playwright / Chromium)
    │  Fetches full page content from JS-heavy sites
    │  Stops after 3 successful pages
    │
    ▼  SUMMARIZE  (LLM)
    │  One summary per crawled page
    │
    ▼  MERGE  (LLM)
    │  Synthesises all summaries into a final report
```

---

## Project Structure

```
totemengine/
├── main.py                # Entrypoint — dispatches to CLI or server
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Compose stacks (cli, server)
├── pyproject.toml         # Python package metadata
├── requirements.txt       # Pinned dependencies
├── .env.example           # Environment variable template
│
├── totem/
│   ├── __init__.py
│   ├── config.py          # Env vars + SUPPORTED_MODELS dict
│   ├── llm.py             # LLM client factory (Mistral, Groq)
│   ├── models.py          # Shared Pydantic models
│   ├── nodes.py           # LangGraph node implementations
│   ├── graph.py           # LangGraph workflow definition + orchestrator
│   ├── crawl_client.py    # Playwright headless Chromium scraper
│   ├── cli.py             # argparse CLI (research, models, server)
│   └── server.py          # FastAPI REST API
│
└── docs/
    ├── DOCKER.md          # Docker-only deployment guide
    ├── CONFIGURATION.md   # Environment variables and settings
    ├── ARCHITECTURE.md    # This file
    ├── API.md             # REST API reference
    └── CONTRIBUTING.md    # Development setup
```

---

## Layer by Layer

### 1. Entrypoint — `main.py`

Dispatches to CLI subcommands:

```bash
python main.py research "query"        # run pipeline
python main.py models                  # list providers
python main.py server --port 8000      # start API
```

### 2. CLI — `totem/cli.py`

Argparse-based. Maps subcommands to:
- `research` → `totem.graph.run_research()`
- `models` → prints `SUPPORTED_MODELS`
- `server` → launches Uvicorn + FastAPI

### 3. Graph — `totem/graph.py`

Defines the LangGraph `StateGraph` with 5 nodes:

```python
builder.add_node("decompose", decompose)
builder.add_node("search", search)
builder.add_node("crawl", crawl)
builder.add_node("summarize", summarize)
builder.add_node("merge", merge)
```

State flows through each node sequentially. `run_research(query, model)` is the public entry point.

### 4. Nodes — `totem/nodes.py`

Each node receives the graph state, performs one task, and returns the updated state.

| Node | Input | Output |
|------|-------|--------|
| `decompose` | `query` (str) | `sub_queries` (list[str]) |
| `search` | `sub_queries` | `search_results` (list[dict]) |
| `crawl` | `search_results` | `crawled_contents` (list[dict]) |
| `summarize` | `crawled_contents` | `summaries` (list[str]) |
| `merge` | `summaries`, `sub_queries` | `final_summary` (str) |

### 5. LLM — `totem/llm.py`

Factory that returns a configured ChatModel instance based on:

- `model="mistral"` → `ChatMistralAI` from `langchain_mistralai`
- `model="groq"` → `ChatGroq` from `langchain_groq`

All nodes share the same LLM instance per pipeline run.

### 6. Crawl Client — `totem/crawl_client.py`

Singleton headless Chromium browser:

```python
_browser = None

def _get_browser():
    p = sync_playwright().start()
    _browser = p.chromium.launch(headless=True)
    return _browser
```

The `crawl()` function:
1. Opens a new page for each URL
2. Navigates with 30s timeout, waits for `domcontentloaded`
3. Extracts HTML → strips `<script>`, `<style>`, tags → plain text
4. Caps content at 8000 characters
5. Stops after 3 successful pages

Browser is closed by `graph.py` in a `finally` block.

### 7. Server — `totem/server.py`

FastAPI app with endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/models` | Available providers |
| `POST` | `/research` | Async research (returns `task_id`) |
| `GET` | `/research/{task_id}` | Poll async result |
| `POST` | `/research/sync` | Synchronous research (blocks) |

CORS is open (`allow_origins=["*"]`) for local development.

---

## Data Flow

```
User Query
  │
  ├─► decompose ──► sub_queries (3-5 strings)
  │
  ├─► search ──► search_results (list of {title, url, snippet})
  │
  ├─► crawl ──► crawled_contents (list of {url, content})
  │                content = plain text, max 8000 chars
  │
  ├─► summarize ──► summaries (one per page)
  │
  └─► merge ──► final_summary (coherent report)
```

State is a `dict[str, Any]` passed between nodes. Each node reads relevant keys and writes new ones.

---

## Runtime Details

| Concern | Detail |
|---------|--------|
| Browser | Headless Chromium via Playwright sync API |
| Concurrency | Single-threaded pipeline; server uses background threads for async tasks |
| Timeout | 30s per page, 5-10min full pipeline |
| Memory | ~200MB (Chromium + Python) |
| Persistence | In-memory only (task store is a dict) |

---

## Related

- [DOCKER.md](DOCKER.md) — Deployment
- [CONFIGURATION.md](CONFIGURATION.md) — Settings
- [API.md](API.md) — REST endpoints
