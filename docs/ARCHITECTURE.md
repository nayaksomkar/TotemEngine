# Architecture

WebHunter is a small, focused microservice: **HTTP in → search + crawl → JSON out**. There is no LLM inside the service, no database, and no sibling container. Everything runs in a single Docker image.

## Pipeline Overview

```
User Query (JSON over HTTP)
    │
    ▼  build_search_queries()
    │   Expand query + variants into N search strings.
    │
    ▼  web_search()   (DuckDuckGo via ddgs)
    │   Run each query; dedupe URLs; cap at MAX_RESULTS.
    │
    ▼  crawl_pages()  (Playwright / Chromium)
    │   Fetch up to MAX_PAGES URLs; strip scripts/styles; cap at CONTENT_MAX_CHARS.
    │
    ▼  ResearchResult
    JSON envelope with search_queries, search_results,
    crawled_contents, stats, errors.
```

> **No LLM calls, no LangChain, no LangGraph.** Any "summarize this content" or "synthesize these findings" step is the caller's job (typically CompetitorEngine + LLMPing in the larger architecture).

---

## Project Structure

```
webhunter/
├── main.py                # Entrypoint — `python main.py server`
├── Dockerfile             # Container image definition
├── docker-compose.yml     # Local Compose stack (server only)
├── pyproject.toml         # Python package metadata
├── requirements.txt       # Pinned dependencies
├── .env.example           # Environment variable template
│
├── totem/
│   ├── __init__.py
│   ├── config.py          # Env vars (no API keys)
│   ├── search_client.py   # ddgs wrapper + query expansion
│   ├── crawl_client.py    # Playwright headless Chromium scraper
│   ├── pipeline.py        # run_research() — search → crawl orchestrator
│   ├── models.py          # TypedDicts (SearchResult, CrawledContent, ResearchResult, ...)
│   ├── server.py          # FastAPI HTTP layer
│   └── cli.py             # argparse CLI (only `server`)
│
└── docs/
    ├── DOCKER.md          # Docker & Render deployment
    ├── CONFIGURATION.md   # Environment variables
    ├── ARCHITECTURE.md    # This file
    ├── API.md             # REST API reference
    └── CONTRIBUTING.md    # Local development setup
```

---

## Layer by Layer

### 1. Entrypoint — `main.py`

Single subcommand: `server`.

```bash
python main.py server --host 0.0.0.0 --port 8000
```

The Dockerfile's `CMD ["server"]` invokes the same path; the `PORT` env var is read by `totem.config.PORT` and passed to Uvicorn.

### 2. Config — `totem/config.py`

Pure environment-variable configuration. No secrets — there are no LLM provider keys. Numeric vars (`PORT`, `MAX_RESULTS`, `MAX_PAGES`, `PAGE_TIMEOUT_MS`, `CONTENT_MAX_CHARS`) tolerate empty/invalid values and fall back to documented defaults.

### 3. Search — `totem/search_client.py`

`build_search_queries(query, variants)` expands one user query into a list:

```
"EV market 2025" + ["pricing", "competitors"]
  → ["EV market 2025",
     "EV market 2025 pricing",
     "EV market 2025 competitors"]
```

`web_search(...)` runs each query through `ddgs.DDGS().text(...)`, deduplicates by URL, and stops once `max_results` is reached. Per-query failures are logged and skipped — one bad query does not abort the whole pipeline.

### 4. Crawl — `totem/crawl_client.py`

Singleton headless Chromium, identical to the previous TotemEngine implementation:

```python
_browser = None

def _get_browser():
    p = sync_playwright().start()
    _browser = p.chromium.launch(headless=True)
    return _browser
```

The `crawl()` function:

1. Opens a new page for each URL.
2. Navigates with `PAGE_TIMEOUT_MS` timeout, waits for `domcontentloaded`.
3. Extracts HTML → strips `<script>`, `<style>`, tags → plain text.
4. Caps each page at `CONTENT_MAX_CHARS` characters.
5. Stops after `MAX_PAGES` successful fetches.

The browser is closed by `pipeline.shutdown()` (and by FastAPI's `shutdown` event handler).

### 5. Pipeline — `totem/pipeline.py`

`run_research(query, options) -> ResearchResult` is the only public entry point. It:

1. Builds the search-query list.
2. Calls `web_search(...)`.
3. Calls `crawl(...)` for the collected URLs.
4. Assembles the `ResearchResult` dict, including `stats` (counts, elapsed ms) and `errors` (per-stage failures).

The function is synchronous from the caller's perspective; internal Playwright work runs on a dedicated asyncio loop in a background thread (existing pattern from the previous codebase).

### 6. Server — `totem/server.py`

A thin FastAPI wrapper around `pipeline.run_research`. Four routes, no business logic:

| Method | Path | Behavior |
|--------|------|----------|
| `GET`  | `/health` | Returns `{"status":"ok"}` |
| `POST` | `/research/sync` | Runs pipeline synchronously, returns `ResearchResult` |
| `POST` | `/research` | Spawns background thread, returns `{task_id, status:"running"}` |
| `GET`  | `/research/{task_id}` | Returns stored task result (in-memory) |

CORS is open (`allow_origins=["*"]`) for ease of local development; tighten in production.

---

## Data Flow

```
JSON request
  │
  ├─► search_client.build_search_queries()  ──► list[str]
  │
  ├─► search_client.web_search()             ──► list[SearchResult]
  │                                              {sub_query, url, title, snippet}
  │
  ├─► crawl_client.crawl()                   ──► list[CrawledContent]
  │                                              {url, sub_query, title, content}
  │
  └─► pipeline.run_research()                ──► ResearchResult
                                                 {status, query, search_queries,
                                                  search_results, crawled_contents,
                                                  stats, errors}
```

---

## Runtime Details

| Concern | Detail |
|---------|--------|
| Browser | Headless Chromium via Playwright async API (single instance, reuse across requests) |
| Concurrency | One pipeline at a time per process; async tasks use background threads |
| Timeout | `PAGE_TIMEOUT_MS` (default 30s) per page |
| Memory | ~200MB idle (Chromium + Python) |
| Persistence | In-memory only (`tasks` dict) |
| LLM calls | **None** |

---

## Failure Handling

The pipeline is built for partial success. Each stage catches exceptions:

- **Search failures** (rate limits, network blips) are caught per-query; the remaining queries still run. Any error is recorded in `errors[]` with `stage: "search"`.
- **Crawl failures** (timeouts, navigation errors) are caught per-URL; the remaining URLs still attempt. Errors are recorded in `errors[]` with `stage: "crawl"`.
- The response HTTP status is **200** in both success and partial-failure cases. The body's `status` field is `"completed"` (at least one page crawled) or `"failed"` (zero pages crawled and at least one error occurred).
- A hard 500 is returned only if the pipeline raises an unexpected exception that escapes the outer `try`/`except` blocks.

This makes WebHunter easy for service-to-service callers: they always parse a `ResearchResult` shape and decide what to do with partial data.

---

## External Integration

WebHunter assumes it is called by a trusted internal microservice (e.g. CompetitorEngine) over a private network. There is no authentication layer; add `Authorization` headers / a reverse-proxy gateway before exposing the service publicly.

---

## Related

- [API.md](API.md) — Full REST contract
- [DOCKER.md](DOCKER.md) — Deployment
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables
