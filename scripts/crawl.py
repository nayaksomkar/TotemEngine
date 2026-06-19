"""
Crawl URLs using the crawl4ai REST API.

Usage:
    python scripts/crawl.py https://example.com

Requires: requests (pip install requests)
The crawl4ai container must be running (docker compose up -d).
"""

import requests
import json
import time

API_URL = "http://localhost:11235"


def health():
    """Check if the container and API are healthy."""
    resp = requests.get(f"{API_URL}/health")
    return resp.json()


def submit(url: str, priority: int = 10):
    """Submit a crawl job and return the task ID."""
    resp = requests.post(
        f"{API_URL}/crawl",
        json={"urls": [url], "priority": priority}
    )
    resp.raise_for_status()
    return resp.json()


def get_task(task_id: str):
    """Poll for the result of a submitted crawl task."""
    resp = requests.get(f"{API_URL}/task/{task_id}")
    resp.raise_for_status()
    return resp.json()


def dashboard():
    """Fetch monitoring dashboard data (requires container running)."""
    resp = requests.get(f"{API_URL}/dashboard")
    resp.raise_for_status()
    return resp.text


def crawl(url: str, priority: int = 10, poll_interval: float = 2.0, timeout: float = 60.0):
    """Submit a crawl job and wait (poll) for the result."""
    data = submit(url, priority)

    if "results" in data:
        return data["results"]

    task_id = data["task_id"]
    start = time.time()
    while True:
        result = get_task(task_id)
        status = result.get("status")
        if status == "completed":
            return result
        if time.time() - start > timeout:
            raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
        time.sleep(poll_interval)


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

    print(f"Health: {health()}\n")
    result = crawl(url)
    print(json.dumps(result, indent=2))
