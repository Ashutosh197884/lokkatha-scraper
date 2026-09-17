"""Headless browser crawler using Playwright to drive real Chrome/Chromium.

Renders client-side JavaScript pages that the plain HTTP client cannot
(SPA shells, JS-rendered articles). System Google Chrome is used when
installed; the Playwright-bundled chromium is the fallback.
"""

import hashlib
from pathlib import Path
from typing import Optional

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.schemas.crawl import CrawlResult
from app.utils.urls import extract_domain, normalize_url

logger = get_logger("crawler.browser")


class BrowserCrawler:
    """Headless browser crawler for rendering client-side JavaScript pages."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._playwright = None
        self._browser = None

    async def fetch(self, url: str) -> CrawlResult:
        """Render page in a real browser and extract final DOM content."""
        norm_url = normalize_url(url)
        domain = extract_domain(norm_url)
        logger.info("browser_crawl_requested", url=norm_url)
        try:
            html = await self._render(norm_url)
        except Exception as exc:  # noqa: BLE001 — any browser failure becomes a failed result
            logger.warning("browser_crawl_failed", url=norm_url, error=str(exc))
            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                requires_browser=True,
                is_success=False,
                error=f"browser: {exc}",
            )
        if not html:
            return CrawlResult(
                url=url,
                normalized_url=norm_url,
                domain=domain,
                requires_browser=True,
                is_success=False,
                error="browser: empty page after render",
            )
        content_hash = hashlib.sha256(html.encode("utf-8")).hexdigest()

        # Persist post-JS HTML exactly like the HTTP path so link discovery
        # and the extraction pipeline can consume it from raw_html_path.
        raw_path = None
        if self.settings.crawler.save_raw_html:
            raw_dir = Path(self.settings.storage.raw_dir)
            try:
                raw_dir.mkdir(parents=True, exist_ok=True)
                raw_file = raw_dir / f"{content_hash}.html"
                raw_file.write_text(html, encoding="utf-8", errors="replace")
                raw_path = str(raw_file)
            except OSError as exc:
                logger.warning("failed_to_save_raw_html", url=norm_url, error=str(exc))

        return CrawlResult(
            url=url,
            normalized_url=norm_url,
            domain=domain,
            status_code=200,
            content_type="text/html",
            response_headers={"x-rendered-by": "browser"},
            content_hash=content_hash,
            requires_browser=True,
            is_success=True,
            raw_html_path=raw_path,
        )

    async def _render(self, url: str) -> str:
        """Launch once per crawl, reuse the browser, return post-JS HTML."""
        await self._ensure_browser()
        page = await self._browser.new_page()
        try:
            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.settings.browser.timeout_seconds * 1000,
            )
            if response is not None and response.status >= 400:
                raise RuntimeError(f"HTTP {response.status}")
            await page.wait_for_timeout(1500)  # ponytail: fixed JS settle window, not a scheduler
            return await page.content()
        finally:
            await page.close()

    async def _ensure_browser(self) -> None:
        """Start Playwright once; prefer installed Chrome, then bundled chromium."""
        if self._browser is not None:
            return
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        headless = self.settings.browser.headless
        try:
            self._browser = await self._playwright.chromium.launch(
                channel="chrome", headless=headless
            )
            logger.info("browser_launched", channel="chrome")
        except Exception:
            self._browser = await self._playwright.chromium.launch(headless=headless)
            logger.info("browser_launched", channel="chromium")

    async def close(self) -> None:
        """Tear down browser and Playwright driver if they were started."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright is not None:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None
