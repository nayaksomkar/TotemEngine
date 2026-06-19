from typing import TypedDict, Optional


class SearchResult(TypedDict):
    sub_query: str
    url: str
    title: str
    snippet: str


class CrawledContent(TypedDict):
    url: str
    content: str
    sub_query: str


class ResearchState(TypedDict):
    query: str
    sub_queries: list
    search_results: list
    crawled_contents: list
    summaries: list
    final_summary: str
    model_choice: str
    error: Optional[str]
