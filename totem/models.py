# ---------------------------------------------------------------------------
# Models — TypedDict definitions used throughout the LangGraph pipeline.
# These define the shape of state passed between graph nodes.
# ---------------------------------------------------------------------------

from typing import TypedDict, Optional


# A single web search result with metadata about the page found.
class SearchResult(TypedDict):
    sub_query: str   # The sub-query that produced this result
    url: str         # Full URL of the page
    title: str       # Page title from search engine
    snippet: str     # Short description from search results


# Content fetched from a crawled web page.
class CrawledContent(TypedDict):
    url: str         # Source URL
    content: str     # Cleaned page text (up to 8000 chars)
    sub_query: str   # Which sub-query this content belongs to


# The full state object passed through every LangGraph node.
# Each key is mutated by a specific node in the pipeline.
class ResearchState(TypedDict):
    query: str                     # Original user question
    sub_queries: list[str]         # Broken-down sub-queries (from decompose)
    search_results: list[SearchResult]   # URLs found (from search)
    crawled_contents: list[CrawledContent]  # Page text (from crawl)
    summaries: list[str]           # Per-page LLM summaries (from summarize)
    final_summary: str             # Merged research report (from merge)
    model_choice: str              # Which LLM provider to use ("mistral" | "groq")
    error: Optional[str]           # Any error message from the pipeline
