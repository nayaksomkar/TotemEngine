# ---------------------------------------------------------------------------
# LangGraph Workflow — defines the 5-node research pipeline.
#
# The graph runs in this order:
#   START → decompose → search → crawl → summarize → merge → END
#
# Each node reads from and writes to a shared ResearchState object.
# ---------------------------------------------------------------------------

import logging

from langgraph.graph import StateGraph, START, END

from totem.models import ResearchState
from totem.crawl_client import close as close_browser
from totem.nodes import (
    decompose_query,
    web_search,
    crawl_pages,
    summarize_pages,
    merge_summaries,
)

logger = logging.getLogger(__name__)


def build_research_graph() -> StateGraph:
    """
    Build and compile the LangGraph StateGraph for the research pipeline.

    The graph is a linear chain of 5 nodes:
      1. decompose    —  break query into sub-queries
      2. search       —  DuckDuckGo for each sub-query
       3. crawl        —  fetch page content (Playwright / Chromium)
      4. summarize    —  LLM summary per page
      5. merge        —  combine into final report
    """
    graph = StateGraph(ResearchState)

    # Register all nodes with the graph
    graph.add_node("decompose", decompose_query)
    graph.add_node("search", web_search)
    graph.add_node("crawl", crawl_pages)
    graph.add_node("summarize", summarize_pages)
    graph.add_node("merge", merge_summaries)

    # Define the linear execution flow
    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "search")
    graph.add_edge("search", "crawl")
    graph.add_edge("crawl", "summarize")
    graph.add_edge("summarize", "merge")
    graph.add_edge("merge", END)

    return graph.compile()


def _build_initial_state(query: str, model_choice: str = "mistral") -> ResearchState:
    return {
        "query": query,
        "sub_queries": [],
        "search_results": [],
        "crawled_contents": [],
        "summaries": [],
        "final_summary": "",
        "model_choice": model_choice,
        "error": None,
    }


def run_research(query: str, model_choice: str = "mistral") -> ResearchState:
    """
    Convenience wrapper: build the graph, create initial state, and invoke.

    Args:
        query:         The user's research question.
        model_choice:  Which LLM provider to use ("mistral" | "groq").

    Returns:
        The final ResearchState with all fields populated, including
        the final_summary.
    """
    graph = build_research_graph()
    initial_state = _build_initial_state(query, model_choice)

    try:
        result = graph.invoke(initial_state)
        return result
    finally:
        close_browser()


def run_research_stream(query: str, model_choice: str = "mistral"):
    """
    Run the research pipeline and yield (node_name, state_update) for each
    completed node.  The caller receives progress updates in real time.
    """
    graph = build_research_graph()
    initial_state = _build_initial_state(query, model_choice)
    final_state = None

    accumulated = dict(initial_state)
    try:
        for event in graph.stream(initial_state, stream_mode="updates"):
            for node_name, state_update in event.items():
                accumulated.update(state_update)
                yield node_name, state_update
    finally:
        close_browser()

    yield "result", accumulated
