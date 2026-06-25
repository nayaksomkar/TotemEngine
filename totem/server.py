# ---------------------------------------------------------------------------
# FastAPI Server — REST API for the research pipeline.
#
# Endpoints:
#   GET  /health         Health check
#   GET  /models         List available LLM providers
#   POST /research       Start async research (returns task_id)
#   GET  /research/{id}  Poll async task result
#   POST /research/sync  Run research synchronously (blocking)
# ---------------------------------------------------------------------------

import logging
import uuid
from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from totem.graph import run_research
from totem.config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TotemEngine Research API",
    description="AI-powered research assistant using LangGraph + Playwright",
    version="0.2.0",
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for async task results (simple dict — replace with DB for production)
tasks: dict[str, dict] = {}

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class ResearchRequest(BaseModel):
    query: str                     # The research question
    model: str = "mistral"         # LLM provider name


class ResearchResponse(BaseModel):
    task_id: str                   # Unique ID for polling
    status: str                    # "running" | "completed" | "failed"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    """Simple health check — returns OK if the server is running."""
    return {"status": "ok"}


@app.get("/models")
def list_models():
    """Return a map of available model names to display labels."""
    return {
        name: info["display"]
        for name, info in SUPPORTED_MODELS.items()
    }


@app.post("/research", response_model=ResearchResponse)
def start_research(req: ResearchRequest):
    """
    Start an asynchronous research task.

    The task runs in a background thread.  Poll GET /research/{task_id}
    for the result.
    """
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "running",
        "query": req.query,
        "model": req.model,
    }

    def _run():
        """Background thread that executes the LangGraph pipeline."""
        try:
            result = run_research(req.query, req.model)
            tasks[task_id].update({
                "status": "completed",
                "result": result,
            })
        except Exception as e:
            logger.exception(f"Task {task_id} failed")
            tasks[task_id].update({"status": "failed", "error": str(e)})

    Thread(target=_run, daemon=True).start()
    return ResearchResponse(task_id=task_id, status="running")


@app.get("/research/{task_id}")
def get_research(task_id: str):
    """
    Poll the result of an async research task.

    Returns 404 if the task_id doesn't exist.
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.post("/research/sync")
def research_sync(req: ResearchRequest):
    """
    Run research synchronously and return the full result.

    This blocks until the pipeline completes (may take 30-120 seconds).
    """
    try:
        result = run_research(req.query, req.model)
        return {
            "status": "completed",
            "query": result["query"],
            "sub_queries": result["sub_queries"],
            "summaries": result["summaries"],
            "final_summary": result["final_summary"],
            "model_choice": result["model_choice"],
        }
    except Exception as e:
        logger.exception("Sync research failed")
        raise HTTPException(500, str(e))
