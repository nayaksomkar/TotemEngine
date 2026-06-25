#!/usr/bin/env python3
"""
TotemEngine — AI-powered research assistant.

Decomposes a user query into sub-queries, searches the web, crawls pages
(via Playwright / Chromium), summarizes each source with an LLM, and
synthesises everything into a coherent research report.

Usage:
    # CLI — run research and print to terminal
    python main.py research "How does quantum computing work?" --model mistral

    # CLI — list available models
    python main.py models

    # CLI — start REST API server
    python main.py server --port 8000

    # API — synchronous research
    curl -X POST http://localhost:8000/research/sync \
        -H "Content-Type: application/json" \
        -d '{"query": "your question", "model": "mistral"}'
"""

from totem.cli import main

if __name__ == "__main__":
    main()
