# ---------------------------------------------------------------------------
# WebHunter Search Client
#
# DuckDuckGo-backed web search. No LLM involvement. Produces a deduplicated
# list of SearchResult records given a query and an optional list of
# variant suffixes (e.g. "pricing", "competitors") for breadth.
# ---------------------------------------------------------------------------

import logging
from typing import Iterable

from ddgs import DDGS

from totem.models import SearchResult

logger = logging.getLogger(__name__)


def build_search_queries(query: str, variants: Iterable[str] | None = None) -> list[str]:
    """
    Expand a single user query into a list of search queries.

    The original query is always first. Each variant, if any, is appended
    as a suffix. Empty/duplicate queries are removed while preserving order.

    Example:
        build_search_queries("EV market 2025", ["pricing", "competitors"])
        -> ["EV market 2025", "EV market 2025 pricing", "EV market 2025 competitors"]
    """
    seen: set[str] = set()
    ordered: list[str] = []

    base = (query or "").strip()
    if base and base not in seen:
        seen.add(base)
        ordered.append(base)

    for v in variants or []:
        suffix = (v or "").strip()
        if not suffix:
            continue
        composed = f"{base} {suffix}".strip()
        if composed and composed not in seen:
            seen.add(composed)
            ordered.append(composed)

    return ordered


def web_search(
    query: str,
    variants: Iterable[str] | None = None,
    max_results: int = 6,
    region: str = "wt-wt",
) -> list[SearchResult]:
    """
    Run DuckDuckGo text search for the query plus each variant.

    Stops once `max_results` unique URLs have been collected.

    Returns a list of SearchResult TypedDicts:
        { sub_query, url, title, snippet }
    """
    queries = build_search_queries(query, variants)
    results: list[SearchResult] = []
    seen_urls: set[str] = set()

    with DDGS() as ddgs:
        for sq in queries:
            if len(results) >= max_results:
                break
            try:
                # Per-query cap: leave room so multiple queries contribute.
                per_query = max(2, (max_results - len(results)) // max(1, len(queries) - queries.index(sq)))
                for r in ddgs.text(sq, region=region, max_results=per_query):
                    url = r.get("href", "") or ""
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)
                    results.append(SearchResult(
                        sub_query=sq,
                        url=url,
                        title=r.get("title", ""),
                        snippet=r.get("body", ""),
                    ))
                    if len(results) >= max_results:
                        break
            except Exception as e:
                logger.warning(f"Search failed for '{sq}': {e}")

    logger.info(f"Found {len(results)} search results across {len(queries)} queries")
    return results
