# Configuration

All configuration is via environment variables loaded from a `.env` file at the project root. When running with Docker Compose, this happens automatically.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | For `mistral` model | — | Mistral AI API key. Get one at [console.mistral.ai](https://console.mistral.ai/) |
| `GROQ_API_KEY` | For `groq` model | — | Groq API key. Get one at [console.groq.com](https://console.groq.com/) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

> **At least one** of `MISTRAL_API_KEY` or `GROQ_API_KEY` must be set.

## Setting Up `.env`

### Docker (recommended)

```bash
# From the project root
cp .env.example .env
# Edit .env with your keys
nano .env                   # or use any editor
```

Docker Compose reads `.env` automatically on `build` and `up`.

### Non-Docker (development only)

The same `.env` file is loaded by Python-dotenv in [`totem/config.py`](../totem/config.py).

## Model Configuration

Models are defined in [`totem/config.py`](../totem/config.py):

```python
SUPPORTED_MODELS = {
    "mistral": {
        "display": "Mistral AI",
        "provider": "mistral",
        "default_model": "mistral-large-latest",
        "env_key": "MISTRAL_API_KEY",
    },
    "groq": {
        "display": "Groq (Llama 3.3 70B)",
        "provider": "groq",
        "default_model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
    },
}
```

### Changing Models

Edit the `SUPPORTED_MODELS` dict. Each entry requires:
- `display` — human-readable name
- `provider` — LLM provider tag used in [`totem/llm.py`](../totem/llm.py)
- `default_model` — the model ID sent to the provider
- `env_key` — the environment variable holding the API key

## Pipeline Configuration

Hardcoded in [`totem/crawl_client.py`](../totem/crawl_client.py) and [`totem/graph.py`](../totem/graph.py):

| Setting | Value | Where to change |
|---------|-------|-----------------|
| Pages crawled per query | 3 | `crawl_client.py` — `target` parameter |
| Content limit per page | 8000 chars | `crawl_client.py` — slice in results |
| Page timeout | 30 seconds | `crawl_client.py` — `timeout` |
| Wait strategy | `domcontentloaded` | `crawl_client.py` — `wait_until` |
| Sub-queries generated | 3–5 | Controlled by LLM in `nodes.py` |

## Docker Compose Overrides

Edit [`docker-compose.yml`](../docker-compose.yml) to change:

- Image name
- Port mappings
- Environment variable defaults
- Server command arguments (host, port)

## Related

- [DOCKER.md](DOCKER.md) — Running the project
- [ARCHITECTURE.md](ARCHITECTURE.md) — Pipeline structure
- [.env.example](../.env.example) — Template file
