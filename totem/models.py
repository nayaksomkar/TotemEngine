# ---------------------------------------------------------------------------
# WebHunter Models
#
# TypedDicts describing the public data contract returned by the pipeline
# and exposed via the HTTP API.
# ---------------------------------------------------------------------------

from typing import TypedDict, Optional


# A single web search result with metadata about the page found.
class SearchResult(TypedDict):
    sub_query: str   # Which query (original or variant) produced this result
    url: str         # Full URL of the page
    title: str       # Page title from search engine
    snippet: str     # Short description from search results


# Content fetched from a crawled web page.
class CrawledContent(TypedDict):
    url: str         # Source URL
    sub_query: str   # Which query this page was found under
    title: str       # Best-effort title (from search metadata if available)
    content: str     # Cleaned page text (capped at CONTENT_MAX_CHARS)


# A per-stage error that didn't abort the whole pipeline.
class PipelineError(TypedDict):
    stage: str       # "search" | "crawl"
    message: str


class ResearchOptions(TypedDict, total=False):
    max_results: int        # Max URLs collected across all search queries
    max_pages: int          # Max pages actually fetched
    variants: list[str]     # Suffixes appended to the user query for breadth
    region: str             # DuckDuckGo region code
    timeout_ms: int         # Per-page Playwright navigation timeout


class ResearchResult(TypedDict, total=False):
    status: str                    # "completed" | "failed"
    query: str                     # Original user query
    search_queries: list[str]      # All queries actually executed (incl. variants)
    search_results: list[SearchResult]
    crawled_contents: list[CrawledContent]
    stats: dict                    # {search_results_count, crawled_pages_count, elapsed_ms}
    errors: list[PipelineError]
    error: Optional[str]           # Top-level error message if status == "failed"
