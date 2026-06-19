import logging
import uuid
from threading import Thread

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from totem.graph import run_research
from totem.config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TotemEngine Research API",
    description="AI-powered research assistant using LangGraph + crawl4ai",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks: dict[str, dict] = {}


class ResearchRequest(BaseModel):
    query: str
    model: str = "mistral"


class ResearchResponse(BaseModel):
    task_id: str
    status: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    query: str
    sub_queries: list
    summaries: list
    final_summary: str
    model_choice: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def list_models():
    return {
        name: info["display"]
        for name, info in SUPPORTED_MODELS.items()
    }


@app.post("/research", response_model=ResearchResponse)
def start_research(req: ResearchRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "running", "query": req.query, "model": req.model}

    def _run():
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
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.post("/research/sync")
def research_sync(req: ResearchRequest):
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
