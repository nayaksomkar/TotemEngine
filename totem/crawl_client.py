# ---------------------------------------------------------------------------
# WebHunter Crawl Client
#
# Singleton headless Chromium browser (Playwright). Used by pipeline.py
# to fetch full page content from JS-heavy sites.
# ---------------------------------------------------------------------------

import asyncio
import logging
import re
import threading

from totem.config import PAGE_TIMEOUT_MS, CONTENT_MAX_CHARS

logger = logging.getLogger(__name__)

_browser = None
_playwright = None
_loop = asyncio.new_event_loop()
_thread = threading.Thread(target=_loop.run_forever, daemon=True)
_thread.start()


def _run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _loop).result()


async def _get_browser():
    global _browser, _playwright
    if _browser is None:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


def _clean_text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:CONTENT_MAX_CHARS]


async def _crawl(urls: list[str], target: int = 3, timeout_ms: int = PAGE_TIMEOUT_MS) -> list[dict]:
    browser = await _get_browser()
    results: list[dict] = []

    for url in urls:
        if len(results) >= target:
            break
        page = None
        try:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            html = await page.content()
            text = _clean_text(html)
            if text:
                results.append({"url": url, "content": text})
                logger.info(f"  Fetched ({len(results)}/{target}): {url}")
        except Exception as e:
            logger.warning(f"  Failed to fetch {url}: {e}")
        finally:
            if page:
                await page.close()

    return results


def crawl(urls: list[str], target: int = 3, timeout_ms: int = PAGE_TIMEOUT_MS) -> list[dict]:
    """Synchronous wrapper used by the pipeline."""
    return _run_async(_crawl(urls, target=target, timeout_ms=timeout_ms))


async def _close():
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None


def close():
    _run_async(_close())
