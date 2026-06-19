#!/usr/bin/env python3
"""TotemEngine — AI-powered research assistant.

CLI:
    python main.py research "your query" --model mistral
    python main.py models
    python main.py server --port 8000

API:
    curl -X POST http://localhost:8000/research/sync \
        -H "Content-Type: application/json" \
        -d '{"query": "your question", "model": "mistral"}'
"""

from totem.cli import main

if __name__ == "__main__":
    main()
