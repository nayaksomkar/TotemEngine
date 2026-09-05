# ---------------------------------------------------------------------------
# WebHunter Pipeline
#
# The orchestrator for the search → crawl flow. Pure Python — no LangGraph,
# no LLM calls. Returns a structured ResearchResult dict that the HTTP
# server hands back to callers.
# ---------------------------------------------------------------------------

import logging
import time
from typing import Optional

from totem.config import MAX_RESULTS, MAX_PAGES, PAGE_TIMEOUT_MS, SEARCH_VARIANTS
from totem.models import (
    CrawledContent,
    PipelineError,
    ResearchOptions,
    ResearchResult,
    SearchResult,
)
from totem.search_client import build_search_queries, web_search
from totem.crawl_client import crawl as fetch_pages, close as close_browser

logger = logging.getLogger(__name__)


def run_research(
    query: str,
    options: Optional[ResearchOptions] = None,
) -> ResearchResult:
    """
    Run a search-and-crawl pipeline for a single user query.

    Steps:
      1. Expand `query` into one or more search queries (original + variants).
      2. Run DuckDuckGo for each query; dedupe URLs.
      3. Crawl up to `max_pages` URLs with Playwright.

    Returns a ResearchResult dict. On partial failure, populates `errors`
    and continues; only sets `status="failed"` when nothing usable was
    collected.
    """
    opts: ResearchOptions = options or {}
    max_results: int = int(opts.get("max_results", MAX_RESULTS))
    max_pages: int = int(opts.get("max_pages", MAX_PAGES))
    timeout_ms: int = int(opts.get("timeout_ms", PAGE_TIMEOUT_MS))
    region: str = opts.get("region", "wt-wt")
    variants: list[str] = list(opts.get("variants") or SEARCH_VARIANTS)

    errors: list[PipelineError] = []
    started = time.time()

    search_queries = build_search_queries(query, variants)

    # ---- Search ----
    try:
        search_results: list[SearchResult] = web_search(
            query=query,
            variants=variants,
            max_results=max_results,
            region=region,
        )
    except Exception as e:
        logger.exception("Search stage failed entirely")
        errors.append({"stage": "search", "message": str(e)})
        search_results = []

    # ---- Crawl ----
    crawled_contents: list[CrawledContent] = []
    if search_results:
        urls = [r["url"] for r in search_results if r.get("url")]
        url_to_meta = {r["url"]: r for r in search_results}
        try:
            pages = fetch_pages(urls, target=max_pages, timeout_ms=timeout_ms)
            for item in pages:
                content = item.get("content", "")
                url = item.get("url", "")
                if not content or not url:
                    continue
                meta = url_to_meta.get(url, {})
                crawled_contents.append(CrawledContent(
                    url=url,
                    sub_query=meta.get("sub_query", ""),
                    title=meta.get("title", ""),
                    content=content,
                ))
        except Exception as e:
            logger.exception("Crawl stage failed entirely")
            errors.append({"stage": "crawl", "message": str(e)})
    else:
        if not errors:
            errors.append({"stage": "search", "message": "no search results returned"})

    elapsed_ms = int((time.time() - started) * 1000)
    status = "failed" if not crawled_contents and errors else "completed"

    return ResearchResult(
        status=status,
        query=query,
        search_queries=search_queries,
        search_results=search_results,
        crawled_contents=crawled_contents,
        stats={
            "search_results_count": len(search_results),
            "crawled_pages_count": len(crawled_contents),
            "elapsed_ms": elapsed_ms,
        },
        errors=errors,
        error=errors[-1]["message"] if status == "failed" and errors else None,
    )


def shutdown() -> None:
    """Close the Playwright browser. Safe to call multiple times."""
    try:
        close_browser()
    except Exception:
        pass
