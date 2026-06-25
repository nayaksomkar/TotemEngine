# REST API Reference

Start the server:

```bash
docker compose up server
```

The API is available at `http://localhost:8000`.

> By default the container binds to `0.0.0.0:8000`.  
> Change the port in [`docker-compose.yml`](../docker-compose.yml) if needed.

---

## Endpoints

### `GET /health`

Health check.

**Response:**

```json
{ "status": "ok" }
```

---

### `GET /models`

List available LLM providers.

**Response:**

```json
{
  "mistral": "Mistral AI",
  "groq": "Groq (Llama 3.3 70B)"
}
```

---

### `POST /research`

Start an asynchronous research task.

**Request body:**

```json
{
  "query": "How does quantum computing work?",
  "model": "mistral"
}
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `query` | Yes | — | Your research question |
| `model` | No | `mistral` | Provider: `mistral` or `groq` |

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running"
}
```

**Poll for result:**

```bash
curl http://localhost:8000/research/550e8400-e29b-41d4-a716-446655440000
```

**Response when completed:**

```json
{
  "status": "completed",
  "query": "How does quantum computing work?",
  "model": "mistral",
  "result": {
    "query": "...",
    "sub_queries": ["..."],
    "crawled_contents": [{"url": "...", "content": "..."}],
    "summaries": ["..."],
    "final_summary": "...",
    "model_choice": "mistral-large-latest"
  }
}
```

---

### `GET /research/{task_id}`

Poll for async task result.

| Param | Description |
|-------|-------------|
| `task_id` | UUID returned from `POST /research` |

**Responses:**

- `200` — Task found (may be `running`, `completed`, or `failed`)
- `404` — Task not found

**Running task:**

```json
{ "status": "running", "query": "...", "model": "..." }
```

**Completed task:**

```json
{
  "status": "completed",
  "query": "...",
  "model": "...",
  "result": { ... }
}
```

**Failed task:**

```json
{
  "status": "failed",
  "error": "MISTRAL_API_KEY not set"
}
```

---

### `POST /research/sync`

Run research synchronously. Blocks until the pipeline completes (~30-120 seconds).

**Request body:**

```json
{
  "query": "How does quantum computing work?",
  "model": "mistral"
}
```

**Response:**

```json
{
  "status": "completed",
  "query": "How does quantum computing work?",
  "sub_queries": [
    "What is quantum computing?",
    "How do quantum bits (qubits) work?",
    "Current applications of quantum computing"
  ],
  "summaries": [
    "**Source:** https://example.com/1\n\nQuantum computing uses..."
  ],
  "final_summary": "# Research Report\n\n## Introduction\n\n...",
  "model_choice": "mistral-large-latest"
}
```

| Field | Description |
|-------|-------------|
| `sub_queries` | Decomposed sub-questions |
| `crawled_contents` | Raw page URLs (excluded from sync response for brevity) |
| `summaries` | Per-source summaries |
| `final_summary` | Synthesised report in Markdown |
| `model_choice` | Actual model ID used |

---

## Error Responses

All errors return JSON:

```json
{ "detail": "Error message" }
```

Common status codes:

| Code | Cause |
|------|-------|
| `400` | Invalid request body |
| `404` | Task ID not found |
| `500` | Pipeline failure (LLM error, network error, etc.) |

---

## Related

- [DOCKER.md](DOCKER.md) — Running the server
- [CONFIGURATION.md](CONFIGURATION.md) — Environment setup
