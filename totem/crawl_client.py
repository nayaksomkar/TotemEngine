import requests
import time
import logging

from totem.config import CRAWL4AI_URL

logger = logging.getLogger(__name__)


def check_health() -> bool:
    try:
        resp = requests.get(f"{CRAWL4AI_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def submit(urls: list[str], priority: int = 10) -> dict:
    resp = requests.post(
        f"{CRAWL4AI_URL}/crawl",
        json={"urls": urls, "priority": priority},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_task(task_id: str) -> dict:
    resp = requests.get(f"{CRAWL4AI_URL}/task/{task_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def crawl(
    urls: list[str],
    priority: int = 10,
    poll_interval: float = 2.0,
    timeout: float = 120.0,
) -> list[dict]:
    data = submit(urls, priority)
    if "results" in data:
        return data["results"]
    task_id = data.get("task_id")
    if not task_id:
        return []
    start = time.time()
    while True:
        result = get_task(task_id)
        status = result.get("status")
        if status == "completed":
            return result.get("results", [])
        if time.time() - start > timeout:
            logger.warning(f"Task {task_id} timed out after {timeout}s")
            return []
        time.sleep(poll_interval)
