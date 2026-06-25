# ---------------------------------------------------------------------------
# Playwright Web Scraper
#
# Fetches full page content using Playwright (headless Chromium).
# Handles JavaScript-heavy sites (React, Next.js, etc.).
#
# Usage:
#   from totem.crawl_client import crawl
#   results = crawl(["https://example.com"])
#
# First-time setup:
#   pip install playwright
#   playwright install chromium
# ---------------------------------------------------------------------------

import logging
import re

logger = logging.getLogger(__name__)

# Lazy browser instance shared across calls
_browser = None


def _get_browser():
    """Launch or return the shared headless Chromium instance."""
    global _browser
    if _browser is None:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        _browser = p.chromium.launch(headless=True)
    return _browser


def _clean_text(html: str) -> str:
    """Strip tags, scripts, and collapse whitespace into plain text."""
    # Remove script and style blocks
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    # Remove all tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:8000]


def crawl(
    urls: list[str],
    *,
    target: int = 3,
) -> list[dict]:
    """
    Fetch page content using Playwright, stopping after *target* successful
    fetches.  URLs beyond the first batch are tried when earlier ones fail.

    Args:
        urls:   List of URLs to scrape (ordered by priority).
        target: Stop after this many successful pages (default 3).

    Returns:
        A list of dicts: [{"url": str, "content": str}, ...]
    """
    browser = _get_browser()
    results = []

    for url in urls:
        if len(results) >= target:
            break
        page = None
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = page.content()
            text = _clean_text(html)
            if text:
                results.append({"url": url, "content": text})
                logger.info(f"  Fetched ({len(results)}/{target}): {url}")
        except Exception as e:
            logger.warning(f"  Failed to fetch {url}: {e}")
        finally:
            if page:
                page.close()

    return results


def close():
    """Close the shared browser instance (call on shutdown)."""
    global _browser
    if _browser:
        _browser.close()
        _browser = None
