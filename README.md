<div align="center">

# TotemEngine

**AI-powered research assistant** — decompose, search, crawl, summarize, synthesize.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/langgraph-%F0%9F%94%97-1f2937?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.137+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Mistral AI](https://img.shields.io/badge/mistral--ai-ff6f00?logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptMCAxOGMtNC40MSAwLTgtMy41OS04LTggMC00LjQxIDMuNTktOCA4LThzOCAzLjU5IDggOGMwIDQuNDEtMy41OSA4LTggOHoiIGZpbGw9IndoaXRlIi8+PC9zdmc+)](https://mistral.ai)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-crawl4ai-2496ED?logo=docker&logoColor=white)](https://github.com/unclecode/crawl4ai)

<br>

**CLI** · **REST API** · **LangGraph pipeline** · **crawl4ai web scraping**

</div>

---

## Features

- **Query Decomposition** — LLM breaks down your question into 3-5 focused sub-queries.
- **Web Research** — Searches the web for each sub-query via DuckDuckGo.
- **Smart Crawling** — Fetches page content via **crawl4ai** Docker container with automatic fallback to HTTP + BeautifulSoup.
- **Per-Page Summarization** — Each source is independently summarized by the LLM.
- **Synthesis** — All summaries are merged into one coherent research report.
- **Dual Interface** — Terminal-friendly **CLI** and production-ready **REST API** via FastAPI.
- **Model Selection** — Choose between **Mistral AI** and **Groq** at runtime.

---

## Architecture

```
                        ┌──────────────────────┐
                        │    User Query         │
                        │  "How does X work?"   │
                        └──────────┬───────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                     LangGraph StateGraph                           │
│                                                                    │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐   │
│   │DECOMPOSE │    │  SEARCH  │    │  CRAWL   │    │SUMMARIZE  │   │
│   │  Query   ├───►│   Web    ├───►│  Pages   ├───►│  Each     │   │
│   │  → sub-  │    │  → URLs  │    │  → text  │    │  Page     │   │
│   │  queries │    │          │    │          │    │  → summary│   │
│   └──────────┘    └──────────┘    └──────────┘    └─────┬─────┘   │
│                                                          │         │
│                                                   ┌──────▼──────┐ │
│                                                   │    MERGE    │ │
│                                                   │  Summaries  │ │
│                                                   │  → Report   │ │
│                                                   └─────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Final Research      │
                        │   Report              │
                        └──────────────────────┘
```

### LangGraph Nodes

| Node | Function | Input → Output | LLM Call |
|------|----------|---------------|----------|
| `decompose` | `decompose_query()` | Query → 3-5 sub-queries | Yes |
| `search` | `web_search()` | Sub-queries → URLs + snippets | No (DDGS) |
| `crawl` | `crawl_pages()` | URLs → Page content | No (crawl4ai/HTTP) |
| `summarize` | `summarize_pages()` | Content → Per-page summaries | Yes |
| `merge` | `merge_summaries()` | All summaries → Final report | Yes |

---

## Quick Start

### Prerequisites

- Python **3.11+**
- Docker (optional — for crawl4ai; falls back to direct HTTP otherwise)
- API key for [Mistral AI](https://console.mistral.ai/) and/or [Groq](https://console.groq.com/)

### Setup

```bash
# 1. Clone & enter
git clone https://github.com/yourusername/totemengine.git
cd totemengine

# 2. Virtual environment (standard venv, no uv)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install
pip install -e .

# 4. Configure API keys
cp .env.example .env
# Edit .env with your keys:
#   MISTRAL_API_KEY=sk-...
#   GROQ_API_KEY=gsk_...
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | Yes (for `mistral` model) | — | Mistral AI API key |
| `GROQ_API_KEY` | Yes (for `groq` model) | — | Groq API key |
| `CRAWL4AI_URL` | No | `http://localhost:11235` | crawl4ai REST endpoint |
| `LOG_LEVEL` | No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |

---

## Usage

### CLI — Run Research

```bash
# Default (Mistral AI)
python main.py research "How does quantum computing work?"

# With Groq
python main.py research "Best practices for Python APIs" --model groq

# Short flag
python main.py research "Your query" -m groq
```

### CLI — List Models

```bash
python main.py models
```

### CLI — Start API Server

```bash
python main.py server --port 8000
```

### REST API

Once the server is running:

```bash
# Health
curl http://localhost:8000/health

# Available models
curl http://localhost:8000/models

# Synchronous research (blocking)
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "How to get a job at Google?", "model": "mistral"}'

# Async research (returns task_id)
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "How to get a job at Google?", "model": "misral"}'

# Poll async result
curl http://localhost:8000/research/<task_id>
```

### Example Output

```bash
$ python main.py research "Python API best practices"

════════════════════════════════════════════════════════
  TotemEngine — AI-Powered Research Assistant
════════════════════════════════════════════════════════

12:30:01 [INFO] Generated 4 sub-queries
12:30:04 [INFO] Found 12 search results
12:30:10 [INFO] Crawled 10 pages
12:30:18 [INFO] Generated 10 summaries
12:30:22 [INFO] Final summary generated

════════════════════════════════════════════════════════
  SUB-QUERIES
════════════════════════════════════════════════════════
  1. Best practices for designing RESTful APIs in Python
  2. Authentication and authorization in Python APIs
  3. API performance optimization techniques
  4. API documentation tools and standards

════════════════════════════════════════════════════════
  FINAL SYNTHESIS
════════════════════════════════════════════════════════

[Full research report generated by the LLM...]
```

---

## crawl4ai Integration

[crawl4ai](https://github.com/unclecode/crawl4ai) provides production-grade web scraping with Playwright-based browser automation, running in Docker.

```bash
# Start the crawl4ai container
docker compose up -d
```

The pipeline auto-detects crawl4ai on `http://localhost:11235`. If the container isn't running, it falls back to direct HTTP requests with BeautifulSoup.

### How It Works

```
totem/crawl_client.py
  │
  ├── POST /crawl   → submit URLs
  ├── GET /task/{id} → poll for completion
  └── Returns cleaned page content
```

### Run Scripts Inside Container

```bash
./scripts/exec-crawl.sh my_script.py
```

---

## Supported Models

| CLI Name | Provider | Default Model | Key Required |
|----------|----------|---------------|--------------|
| `mistral` | [Mistral AI](https://mistral.ai) | `mistral-large-latest` | `MISTRAL_API_KEY` |
| `groq` | [Groq](https://groq.com) | `mixtral-8x7b-32768` | `GROQ_API_KEY` |

---

## Project Structure

```
totemengine/
├── totem/                        # Main package
│   ├── __init__.py               # Package init
│   ├── config.py                 # Environment & model config
│   ├── models.py                 # TypedDict definitions
│   ├── llm.py                    # LLM factory (Mistral, Groq)
│   ├── nodes.py                  # LangGraph node functions
│   ├── graph.py                  # LangGraph workflow compilation
│   ├── crawl_client.py           # crawl4ai REST API wrapper
│   ├── server.py                 # FastAPI server
│   └── cli.py                    # CLI argument parser
├── scripts/                      # Helper scripts
│   ├── crawl.py                  # Crawl a URL via crawl4ai API
│   └── exec-crawl.sh             # Run scripts in Docker container
├── main.py                       # Entry point
├── docker-compose.yml            # crawl4ai container config
├── pyproject.toml                # Project metadata & dependencies
├── .env.example                  # Environment variable template
├── .gitignore
├── LICENSE
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | LangChain + LangGraph |
| **LLM Providers** | Mistral AI · Groq |
| **Web Search** | DuckDuckGo (via `duckduckgo-search`) |
| **Web Scraping** | crawl4ai (Docker) · BeautifulSoup4 (fallback) |
| **API Server** | FastAPI + Uvicorn |
| **Runtime** | Python 3.11+ |

---

## Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

### Development

```bash
# Editable install
pip install -e .

# Install extra dev tools
pip install pytest ruff mypy
```

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

---

<div align="center">
  <sub>Built with LangChain, LangGraph, FastAPI, and crawl4ai.</sub>
</div>
