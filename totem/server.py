# ---------------------------------------------------------------------------
# WebHunter FastAPI Server
#
# HTTP API exposing the search + crawl pipeline. No LLM, no orchestration —
# call the pipeline directly and return structured JSON.
#
# Endpoints:
#   GET  /health              Health check (for Render)
#   POST /research/sync       Run research synchronously (blocks)
#   POST /research            Start async research (returns task_id)
#   GET  /research/{id}       Poll async task result
# ---------------------------------------------------------------------------

import logging
import uuid
from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from totem.pipeline import run_research, shutdown as shutdown_pipeline

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WebHunter API",
    description="Web search + page crawling microservice (DuckDuckGo + Playwright)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory async task store. Replace with a real backend for production.
tasks: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Research question / topic")
    max_results: int | None = Field(None, ge=1, le=50, description="Max URLs to collect from search")
    max_pages: int | None = Field(None, ge=1, le=20, description="Max pages to actually crawl")
    variants: list[str] | None = Field(None, description="Extra suffixes for search breadth")
    region: str | None = Field(None, description="DuckDuckGo region code (e.g. 'us-en', 'wt-wt')")
    timeout_ms: int | None = Field(None, ge=1000, le=180000, description="Per-page Playwright timeout")


class AsyncStartResponse(BaseModel):
    task_id: str
    status: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


def _build_options(req: ResearchRequest) -> dict:
    opts: dict = {}
    if req.max_results is not None:
        opts["max_results"] = req.max_results
    if req.max_pages is not None:
        opts["max_pages"] = req.max_pages
    if req.variants is not None:
        opts["variants"] = req.variants
    if req.region is not None:
        opts["region"] = req.region
    if req.timeout_ms is not None:
        opts["timeout_ms"] = req.timeout_ms
    return opts


@app.post("/research/sync")
def research_sync(req: ResearchRequest):
    """
    Run research synchronously. Blocks until the pipeline completes
    (typically 15-90s depending on crawl count and page weight).
    """
    try:
        result = run_research(req.query, _build_options(req))
        return result
    except Exception as e:
        logger.exception("Sync research failed")
        raise HTTPException(500, str(e))


@app.post("/research", response_model=AsyncStartResponse)
def start_research(req: ResearchRequest):
    """
    Start an asynchronous research task. Returns immediately with a task_id;
    poll `GET /research/{task_id}` for the result.
    """
    task_id = str(uuid.uuid4())
    opts = _build_options(req)
    tasks[task_id] = {"status": "running", "query": req.query}

    def _run():
        try:
            result = run_research(req.query, opts)
            tasks[task_id].update({"status": result.get("status", "completed"), "result": result})
        except Exception as e:
            logger.exception(f"Async task {task_id} failed")
            tasks[task_id].update({"status": "failed", "error": str(e)})

    Thread(target=_run, daemon=True).start()
    return AsyncStartResponse(task_id=task_id, status="running")


@app.get("/research/{task_id}")
def get_research(task_id: str):
    """Poll the result of an async research task."""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.on_event("shutdown")
def _on_shutdown():
    shutdown_pipeline()
