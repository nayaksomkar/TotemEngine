import logging
import re
import requests
from bs4 import BeautifulSoup

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from totem.models import ResearchState, SearchResult, CrawledContent
from totem.llm import get_llm
from totem.crawl_client import crawl as crawl4ai_crawl, check_health
from totem.config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)

DECOMPOSE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research assistant. Break the user's query into 3-5 specific, "
        "focused sub-queries that can be researched independently on the web. "
        "Return ONLY a numbered list, one sub-query per line.",
    ),
    ("human", "{query}"),
])

SEARCH_QUERY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Given a sub-query, rephrase it into an optimal web search query "
        "(5-10 words). Return ONLY the search query, nothing else.",
    ),
    ("human", "{sub_query}"),
])

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research analyst. Summarize the following web page content "
        "in 3-5 sentences, focusing only on facts relevant to the research topic. "
        "Ignore navigation, ads, and irrelevant content.",
    ),
    ("human", "Topic: {topic}\n\nContent:\n{content}"),
])

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


def _parse_sub_queries(text: str) -> list[str]:
    lines = text.strip().split("\n")
    queries = []
    for line in lines:
        line = line.strip()
        line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
        if line and len(line) > 5:
            queries.append(line)
    return queries[:5]


def _fallback_fetch(url: str, timeout: int = 15) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (compatible; TotemEngine/1.0)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs[:20])
        return text.strip() or soup.get_text(strip=True)[:5000]
    except Exception as e:
        logger.warning(f"Fallback fetch failed for {url}: {e}")
        return ""


def decompose_query(state: ResearchState) -> dict:
    logger.info(f"Decomposing query: {state['query']}")
    llm = get_llm(state.get("model_choice", "mistral"))
    chain = DECOMPOSE_PROMPT | llm | StrOutputParser()
    result = chain.invoke({"query": state["query"]})
    sub_queries = _parse_sub_queries(result)
    logger.info(f"Generated {len(sub_queries)} sub-queries")
    return {"sub_queries": sub_queries}


def web_search(state: ResearchState) -> dict:
    from duckduckgo_search import DDGS
    results: list[SearchResult] = []
    for sq in state["sub_queries"]:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(sq, max_results=3):
                    results.append(SearchResult(
                        sub_query=sq,
                        url=r.get("href", ""),
                        title=r.get("title", ""),
                        snippet=r.get("body", ""),
                    ))
        except Exception as e:
            logger.warning(f"Search failed for '{sq}': {e}")
    logger.info(f"Found {len(results)} search results")
    return {"search_results": results}


def crawl_pages(state: ResearchState) -> dict:
    urls = [r["url"] for r in state["search_results"] if r.get("url")]
    if not urls:
        logger.warning("No URLs to crawl")
        return {"crawled_contents": []}

    contents: list[CrawledContent] = []
    url_to_subquery = {r["url"]: r["sub_query"] for r in state["search_results"]}

    if check_health():
        logger.info("Using crawl4ai for content fetching")
        crawled = crawl4ai_crawl(urls)
        for item in crawled:
            url = item.get("url", "")
            content = item.get("content", "") or item.get("markdown", "") or item.get("text", "")
            if content:
                contents.append(CrawledContent(
                    url=url,
                    content=content[:8000],
                    sub_query=url_to_subquery.get(url, ""),
                ))
    else:
        logger.info("crawl4ai not available, using direct HTTP fallback")

    missing = [u for u in urls if u not in {c["url"] for c in contents}]
    for url in missing:
        content = _fallback_fetch(url)
        if content:
            contents.append(CrawledContent(
                url=url,
                content=content[:8000],
                sub_query=url_to_subquery.get(url, ""),
            ))

    logger.info(f"Crawled {len(contents)} pages")
    return {"crawled_contents": contents}


def summarize_pages(state: ResearchState) -> dict:
    llm = get_llm(state.get("model_choice", "mistral"))
    chain = SUMMARIZE_PROMPT | llm | StrOutputParser()
    summaries = []
    for cc in state["crawled_contents"]:
        try:
            summary = chain.invoke({
                "topic": state["query"],
                "content": cc["content"][:6000],
            })
            summaries.append(f"**Source:** {cc['url']}\n{summary}\n")
        except Exception as e:
            logger.warning(f"Summarization failed for {cc['url']}: {e}")
    logger.info(f"Generated {len(summaries)} summaries")
    return {"summaries": summaries}


def merge_summaries(state: ResearchState) -> dict:
    llm = get_llm(state.get("model_choice", "mistral"))
    chain = MERGE_PROMPT | llm | StrOutputParser()
    summaries_text = "\n\n---\n\n".join(state["summaries"]) if state["summaries"] else "No summaries available."
    try:
        final = chain.invoke({
            "query": state["query"],
            "summaries": summaries_text,
        })
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        final = "Failed to generate final summary."
    return {"final_summary": final}
