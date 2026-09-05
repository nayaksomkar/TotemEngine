# ---------------------------------------------------------------------------
# WebHunter Configuration
#
# All configuration is environment-variable driven. WebHunter has no
# LLM keys, no provider abstractions — just search + crawl tunables.
# ---------------------------------------------------------------------------

import os
from dotenv import load_dotenv

# Load .env from the project root (no-op if missing)
load_dotenv()


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "")
    try:
        return int(raw) if raw else default
    except ValueError:
        return default


# --- Server ---
PORT = _int("PORT", 8000)
HOST = os.getenv("HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Pipeline ---
MAX_RESULTS = _int("MAX_RESULTS", 6)
MAX_PAGES = _int("MAX_PAGES", 3)
PAGE_TIMEOUT_MS = _int("PAGE_TIMEOUT_MS", 30000)
CONTENT_MAX_CHARS = _int("CONTENT_MAX_CHARS", 8000)

# Extra search-query suffixes appended to the user query for breadth.
# Comma-separated. Empty by default — callers pass `variants` per request.
SEARCH_VARIANTS = [v.strip() for v in os.getenv("SEARCH_VARIANTS", "").split(",") if v.strip()]

# --- LLM / Render URLs (kept for reference; WebHunter does not call these directly) ---
# Provided so WebHunter's container can be deployed alongside the other
# microservices and share a single .env. The orchestrator (CompetitorEngine)
# is responsible for talking to LLMPing; WebHunter only reads these as
# informational config.
LLMPING_URL = os.getenv("LLMPING_URL", "https://llmping.onrender.com")
COMPETITOR_ENGINE_URL = os.getenv("COMPETITOR_ENGINE_URL", "https://competitorengine.onrender.com")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "")  # Render sets this on deploy
