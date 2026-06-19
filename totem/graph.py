import logging

from langgraph.graph import StateGraph, START, END

from totem.models import ResearchState
from totem.nodes import (
    decompose_query,
    web_search,
    crawl_pages,
    summarize_pages,
    merge_summaries,
)

logger = logging.getLogger(__name__)


def build_research_graph() -> StateGraph:
    graph = StateGraph(ResearchState)

    graph.add_node("decompose", decompose_query)
    graph.add_node("search", web_search)
    graph.add_node("crawl", crawl_pages)
    graph.add_node("summarize", summarize_pages)
    graph.add_node("merge", merge_summaries)

    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "search")
    graph.add_edge("search", "crawl")
    graph.add_edge("crawl", "summarize")
    graph.add_edge("summarize", "merge")
    graph.add_edge("merge", END)

    return graph.compile()


def run_research(query: str, model_choice: str = "mistral") -> ResearchState:
    graph = build_research_graph()
    initial_state: ResearchState = {
        "query": query,
        "sub_queries": [],
        "search_results": [],
        "crawled_contents": [],
        "summaries": [],
        "final_summary": "",
        "model_choice": model_choice,
        "error": None,
    }
    result = graph.invoke(initial_state)
    return result
