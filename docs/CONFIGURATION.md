# Configuration

All WebHunter configuration is via environment variables, loaded from a `.env` file at the project root. Docker Compose reads this file automatically.

> WebHunter has **no LLM provider keys**. There is nothing secret to manage.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `8000` | Server bind port. Render sets this automatically. |
| `HOST` | No | `0.0.0.0` | Server bind host. |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. `DEBUG`, `INFO`, `WARNING`, `ERROR`. |
| `MAX_RESULTS` | No | `6` | Max URLs collected across all search queries for a single research request. |
| `MAX_PAGES` | No | `3` | Max pages actually fetched (crawled) per research request. |
| `PAGE_TIMEOUT_MS` | No | `30000` | Per-page Playwright navigation timeout in milliseconds. |
| `CONTENT_MAX_CHARS` | No | `8000` | Cap on extracted text per page, in characters. |
| `SEARCH_VARIANTS` | No | _empty_ | Comma-separated extra query suffixes applied to every request unless overridden by the caller. |

### Tuning guidelines

| Scenario | Suggested values |
|----------|------------------|
| Quick market scan | `MAX_PAGES=2`, `MAX_RESULTS=4` |
| Deep competitor analysis | `MAX_PAGES=5`, `MAX_RESULTS=10`, `PAGE_TIMEOUT_MS=60000` |
| Cheap health probes | `MAX_PAGES=1`, `MAX_RESULTS=2` |

---

## Setting Up `.env`

### Docker (recommended)

```bash
cp .env.example .env
nano .env  # edit values
```

Docker Compose reads `.env` automatically on `build` and `up`.

### Non-Docker (development only)

The same `.env` file is loaded by `python-dotenv` in [`totem/config.py`](../totem/config.py).

---

## Request-Level Overrides

Every variable above (except `HOST`, `LOG_LEVEL`) can be overridden **per request** via the JSON body of `/research/sync` or `/research`:

```json
{
  "query": "AI chip manufacturers",
  "max_results": 8,
  "max_pages": 4,
  "variants": ["pricing", "suppliers"],
  "region": "us-en",
  "timeout_ms": 45000
}
```

| Request field | Overrides |
|---------------|-----------|
| `max_results` | `MAX_RESULTS` |
| `max_pages` | `MAX_PAGES` |
| `variants` | `SEARCH_VARIANTS` (per-call list, not merged) |
| `region` | n/a (request-only — DuckDuckGo region code) |
| `timeout_ms` | `PAGE_TIMEOUT_MS` |

---

## Related

- [API.md](API.md) — Request/response shapes
- [DOCKER.md](DOCKER.md) — Docker & Render deployment
- [.env.example](../.env.example) — Template file
