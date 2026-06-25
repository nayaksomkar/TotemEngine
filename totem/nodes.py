# ---------------------------------------------------------------------------
# LangGraph Nodes
#
# Each function here is a LangGraph node.  They receive the current
# ResearchState and return a dict of updates to merge into the state.
#
# Pipeline order:
#   decompose → search → crawl → summarize → merge
# ---------------------------------------------------------------------------

import logging
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from totem.models import ResearchState, SearchResult, CrawledContent
from totem.llm import get_llm
from totem.crawl_client import crawl as fetch_pages
from totem.config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LLM Prompts
# ---------------------------------------------------------------------------

# Prompt 1: Break the user's question into independent researchable sub-queries.
DECOMPOSE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research assistant. Break the user's query into 3-5 specific, "
        "focused sub-queries that can be researched independently on the web. "
        "Return ONLY a numbered list, one sub-query per line.",
    ),
    ("human", "{query}"),
])

# Prompt 2: (Unused directly — kept for future use) Rephrase sub-query for search.
SEARCH_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Given a sub-query, rephrase it into an optimal web search query "
        "(5-10 words). Return ONLY the search query, nothing else.",
    ),
    ("human", "{sub_query}"),
])

# Prompt 3: Summarize a single page's content relative to the research topic.
SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research analyst. Summarize the following web page content "
        "in 3-5 sentences, focusing only on facts relevant to the research topic. "
        "Ignore navigation, ads, and irrelevant content.",
    ),
    ("human", "Topic: {topic}\n\nContent:\n{content}"),
])

# Prompt 4: Merge all individual page summaries into one coherent report.
MERGE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research synthesis expert. Combine the following individual "
        "summaries into a single coherent, well-structured research report. "
        "Organize by topic, use clear headings, and cite sources where applicable. "
        "Be comprehensive but concise.",
    ),
    ("human", "Original Query: {query}\n\nSummaries:\n{summaries}"),
])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_sub_queries(text: str) -> list[str]:
    """
    Convert the LLM's numbered-list output into a clean list of strings.

    Handles formats like:
        "1. First query
         2. Second query
         3. Third query"
    """
    lines = text.strip().split("\n")
    queries = []
    for line in lines:
        line = line.strip()
        # Strip leading number + delimiter:  "1. ", "2) ", etc.
        line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if line and len(line) > 5:
            queries.append(line)
    return queries[:5]


# ---------------------------------------------------------------------------
# LangGraph Nodes  (each returns a dict of state updates)
# ---------------------------------------------------------------------------


def decompose_query(state: ResearchState) -> dict:
    """
    NODE 1/5 — Decompose Query.

    Sends the user's original question to the LLM and asks it to produce
    3-5 independent sub-queries that can be researched separately.
    """
    logger.info(f"Decomposing query: {state['query']}")

    llm = get_llm(state.get("model_choice", "mistral"))
    chain = DECOMPOSE_PROMPT | llm | StrOutputParser()

    result = chain.invoke({"query": state["query"]})
    sub_queries = _parse_sub_queries(result)

    logger.info(f"Generated {len(sub_queries)} sub-queries")
    return {"sub_queries": sub_queries}


MAX_RESULTS = 6  # gather enough URLs to find 3 good pages


def web_search(state: ResearchState) -> dict:
    """
    NODE 2/5 — Web Search.

    For each sub-query, runs a DuckDuckGo search. Stops early once
    enough URLs have been collected (MAX_RESULTS).
    """
    from ddgs import DDGS

    results: list[SearchResult] = []

    for sq in state["sub_queries"]:
        if len(results) >= MAX_RESULTS:
            break
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(sq, max_results=3):
                    results.append(SearchResult(
                        sub_query=sq,
                        url=r.get("href", ""),
                        title=r.get("title", ""),
                        snippet=r.get("body", ""),
                    ))
                    if len(results) >= MAX_RESULTS:
                        break
        except Exception as e:
            logger.warning(f"Search failed for '{sq}': {e}")

    logger.info(f"Found {len(results)} search results")
    return {"search_results": results}


TARGET_PAGES = 3  # stop after this many successful crawls


def crawl_pages(state: ResearchState) -> dict:
    """
    NODE 3/5 — Crawl Pages.

    Fetches page content for each URL using Playwright (headless Chromium).
    Handles JS-heavy sites. Passes all collected URLs; crawl() stops after
    TARGET_PAGES (3) successful fetches.
    """
    urls = [r["url"] for r in state["search_results"] if r.get("url")]
    if not urls:
        logger.warning("No URLs to crawl")
        return {"crawled_contents": []}

    url_to_subquery = {r["url"]: r["sub_query"] for r in state["search_results"]}
    contents: list[CrawledContent] = []

    crawled = fetch_pages(urls, target=TARGET_PAGES)
    for item in crawled:
        content = item.get("content", "")
        url = item.get("url", "")
        if content:
            contents.append(CrawledContent(
                url=url,
                content=content[:8000],
                sub_query=url_to_subquery.get(url, ""),
            ))

    if contents:
        logger.info(f"Collected {len(contents)} pages — proceeding to summarize")
    else:
        logger.warning("No pages could be crawled")
    return {"crawled_contents": contents}


def summarize_pages(state: ResearchState) -> dict:
    """
    NODE 4/5 — Summarize Pages.

    For each crawled page, sends the content to the LLM and asks for a
    concise 3-5 sentence summary focused on the research topic.
    """
    llm = get_llm(state.get("model_choice", "mistral"))
    chain = SUMMARIZE_PROMPT | llm | StrOutputParser()

    summaries = []
    for cc in state["crawled_contents"]:
        try:
            summary = chain.invoke({
                "topic": state["query"],
                "content": cc["content"][:6000],  # Cap prompt to 6K chars
            })
            summaries.append(f"**Source:** {cc['url']}\n{summary}\n")
        except Exception as e:
            logger.warning(f"Summarization failed for {cc['url']}: {e}")

    logger.info(f"Generated {len(summaries)} summaries")
    return {"summaries": summaries}


def merge_summaries(state: ResearchState) -> dict:
    """
    NODE 5/5 — Merge Summaries.

    Takes all individual page summaries and asks the LLM to synthesize them
    into a single coherent, well-structured research report with headings
    and source citations.
    """
    llm = get_llm(state.get("model_choice", "mistral"))
    chain = MERGE_PROMPT | llm | StrOutputParser()

    summaries_text = (
        "\n\n---\n\n".join(state["summaries"])
        if state["summaries"]
        else "No summaries available."
    )

    try:
        final = chain.invoke({
            "query": state["query"],
            "summaries": summaries_text,
        })
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        final = "Failed to generate final summary."

    return {"final_summary": final}
