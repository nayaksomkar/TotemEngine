# REST API Reference

Start the server:

```bash
docker compose up server
```

The API is available at `http://localhost:8000` (or whatever `$PORT` is set to).

> The container binds to `0.0.0.0` by default and reads the `PORT` env var.

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/health` | Health check |
| `POST` | `/research/sync` | Run research synchronously (blocks until done) |
| `POST` | `/research` | Start async research (returns `task_id`) |
| `GET`  | `/research/{task_id}` | Poll async task result |

WebHunter has **no LLM provider abstractions** — there is no `/models` endpoint and no streaming endpoint. The caller is responsible for any LLM work.

---

## `GET /health`

Liveness probe (used by Render).

**Response:**

```json
{ "status": "ok" }
```

---

## `POST /research/sync`

Run a full search + crawl pipeline synchronously. Blocks until all pages have been fetched (typically 15–90 seconds).

**Request body:**

```json
{
  "query": "electric vehicle market leaders 2025",
  "max_results": 6,
  "max_pages": 3,
  "variants": ["pricing", "competitors", "market share"],
  "region": "us-en",
  "timeout_ms": 30000
}
```

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `query` | string | **Yes** | — | The research question. |
| `max_results` | int | No | `6` | Max URLs collected across all search queries. Range 1–50. |
| `max_pages` | int | No | `3` | Max pages actually fetched. Range 1–20. |
| `variants` | string[] | No | `[]` | Suffixes appended to the query for breadth (`"pricing"`, `"competitors"`, etc.). Deduped. |
| `region` | string | No | `"wt-wt"` | DuckDuckGo region code (`us-en`, `uk-en`, `wt-wt`, …). |
| `timeout_ms` | int | No | `30000` | Per-page Playwright navigation timeout in ms. Range 1000–180000. |

**Success response (200):**

```json
{
  "status": "completed",
  "query": "electric vehicle market leaders 2025",
  "search_queries": [
    "electric vehicle market leaders 2025",
    "electric vehicle market leaders 2025 pricing",
    "electric vehicle market leaders 2025 competitors",
    "electric vehicle market leaders 2025 market share"
  ],
  "search_results": [
    {
      "sub_query": "electric vehicle market leaders 2025 pricing",
      "title": "Top 10 EV makers — Statista",
      "url": "https://www.statista.com/...",
      "snippet": "Tesla led the global EV market in Q1 2025..."
    }
  ],
  "crawled_contents": [
    {
      "url": "https://www.statista.com/...",
      "sub_query": "electric vehicle market leaders 2025 pricing",
      "title": "Top 10 EV makers",
      "content": "...plain text up to CONTENT_MAX_CHARS chars..."
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

**Partial-failure response (200, `status="failed"`):**

Returned when **no pages were crawled** and at least one stage errored. Partial search results are preserved so the caller can still inspect what was found.

```json
{
  "status": "failed",
  "query": "obscure topic with no results",
  "search_queries": ["obscure topic with no results"],
  "search_results": [],
  "crawled_contents": [],
  "stats": {
    "search_results_count": 0,
    "crawled_pages_count": 0,
    "elapsed_ms": 3120
  },
  "errors": [
    { "stage": "search", "message": "no search results returned" }
  ],
  "error": "no search results returned"
}
```

**Hard-failure response (500):**

Returned only when the pipeline raises an unexpected exception:

```json
{ "detail": "Internal server error" }
```

---

## `POST /research`

Start an asynchronous research task. The task runs in a background thread.

**Request body:** identical to `/research/sync`.

**Response (200):**

```json
{ "task_id": "550e8400-e29b-41d4-a716-446655440000", "status": "running" }
```

---

## `GET /research/{task_id}`

Poll the result of an async task.

| Param | Description |
|-------|-------------|
| `task_id` | UUID returned from `POST /research` |

**Running task (200):**

```json
{ "status": "running", "query": "...", "task_id": "..." }
```

**Completed task (200):**

Same shape as the `/research/sync` success response above, with `result` wrapping the payload:

```json
{
  "task_id": "...",
  "status": "completed",
  "query": "...",
  "result": {
    "status": "completed",
    "search_queries": [...],
    "search_results": [...],
    "crawled_contents": [...],
    "stats": {...},
    "errors": []
  }
}
```

**Failed task (200, `status="failed"`):**

```json
{
  "task_id": "...",
  "status": "failed",
  "error": "playwright crawl failed: timeout on all URLs"
}
```

**Unknown task (404):**

```json
{ "detail": "Task not found" }
```

> Tasks live in an in-memory dict. If Render cycles the container, `task_id` values are lost. Use `/research/sync` if you need durable results.

---

## Caller Example (Microservice Integration)

```python
import httpx

def call_webhunter(query: str, variants: list[str] | None = None) -> dict:
    resp = httpx.post(
        "https://webhunter.onrender.com/research/sync",
        json={"query": query, "variants": variants or [], "max_pages": 3},
        timeout=httpx.Timeout(180.0),
    )
    resp.raise_for_status()
    return resp.json()

data = call_webhunter("lithium-ion battery manufacturers", ["pricing", "competitors"])
for page in data["crawled_contents"]:
    print(page["url"], "→", page["title"])
    # page["content"] is raw text the caller can summarize, embed, or store
```

---

## Error Codes

| Code | Cause |
|------|-------|
| `400` | Invalid request body (missing `query`, out-of-range numeric fields) |
| `404` | Unknown `task_id` |
| `500` | Unhandled pipeline exception |

The pipeline itself is fault-tolerant: search failures are caught per-query, crawl failures are caught per-URL, and partial results are surfaced in the `errors` array of the response body (HTTP `200`).

---

## Related

- [DOCKER.md](DOCKER.md) — Deployment guide (local + Render)
- [CONFIGURATION.md](CONFIGURATION.md) — Environment variables
- [ARCHITECTURE.md](ARCHITECTURE.md) — Pipeline internals
