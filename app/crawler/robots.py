"""Robots.txt parser, caching engine, and sitemap extractor."""

import asyncio
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx

from app.config.logging import get_logger
from app.config.settings import Settings, get_settings
from app.utils.urls import extract_hostname

logger = get_logger("crawler.robots")


class RobotsEntry:
    """Cached robots.txt parser and metadata for a host."""

    def __init__(self, parser: RobotFileParser, sitemaps: List[str], crawl_delay: Optional[float] = None) -> None:
        self.parser = parser
        self.sitemaps = sitemaps
        self.crawl_delay = crawl_delay
        self.timestamp = time.time()

    def is_expired(self, ttl: int) -> bool:
        """Check if cached entry is older than TTL."""
        return (time.time() - self.timestamp) > ttl


class RobotsManager:
    """Fetches, parses, and caches robots.txt rules per host."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.ttl = self.settings.robots.cache_ttl_seconds
        self._cache: Dict[str, RobotsEntry] = {}
        self._lock = asyncio.Lock()

    def _get_robots_url(self, url: str) -> str:
        """Construct the robots.txt URL for a given target URL."""
        parsed = urlparse(url)
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc or extract_hostname(url)
        return f"{scheme}://{netloc}/robots.txt"

    def _extract_sitemaps_and_delay(self, content: str) -> tuple[List[str], Optional[float]]:
        """Extract Sitemap URLs and Crawl-delay from robots.txt content."""
        sitemaps: List[str] = []
        crawl_delay: Optional[float] = None

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                key, val = line.split(":", 1)
                key_lower = key.strip().lower()
                val_clean = val.strip()

                if key_lower == "sitemap":
                    if val_clean:
                        sitemaps.append(val_clean)
                elif key_lower == "crawl-delay":
                    try:
                        crawl_delay = float(val_clean)
                    except ValueError:
                        pass

        return sitemaps, crawl_delay

    async def fetch_and_parse(self, url: str, client: Optional[httpx.AsyncClient] = None) -> RobotsEntry:
        """Fetch and parse robots.txt for the given URL's host."""
        hostname = extract_hostname(url)
        robots_url = self._get_robots_url(url)

        async with self._lock:
            cached = self._cache.get(hostname)
            if cached and not cached.is_expired(self.ttl):
                return cached

        # Fetch outside lock to prevent blocking other hosts
        parser = RobotFileParser()
        parser.set_url(robots_url)
        sitemaps: List[str] = []
        crawl_delay: Optional[float] = None

        try:
            should_close_client = False
            if client is None:
                client = httpx.AsyncClient(
                    timeout=self.settings.crawler.request_timeout,
                    headers={"User-Agent": self.settings.crawler.user_agent},
                    follow_redirects=True,
                )
                should_close_client = True

            try:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    content = response.text
                    parser.parse(content.splitlines())
                    sitemaps, crawl_delay = self._extract_sitemaps_and_delay(content)
                    logger.debug("robots_parsed", hostname=hostname, sitemaps_found=len(sitemaps))
                elif response.status_code in (404, 410):
                    # No robots.txt found -> permit all crawling
                    parser.allow_all = True
                    logger.debug("robots_not_found_allow_all", hostname=hostname, status=response.status_code)
                else:
                    # Non-200, non-404 responses -> permit with caution unless blocked
                    parser.allow_all = True
                    logger.warning("robots_fetch_non_200", hostname=hostname, status=response.status_code)
            finally:
                if should_close_client:
                    await client.aclose()

        except Exception as exc:
            logger.warning("robots_fetch_failed_default_allow", hostname=hostname, error=str(exc))
            parser.allow_all = True

        entry = RobotsEntry(parser, sitemaps, crawl_delay)

        async with self._lock:
            self._cache[hostname] = entry

        return entry

    async def is_allowed(self, url: str, client: Optional[httpx.AsyncClient] = None) -> bool:
        """Check if URL is permitted to be crawled by our configured user agent."""
        if not self.settings.robots.enabled or not self.settings.crawler.respect_robots_txt:
            return True

        hostname = extract_hostname(url)
        if not hostname:
            return True

        entry = await self.fetch_and_parse(url, client=client)
        user_agent = self.settings.crawler.user_agent
        return entry.parser.can_fetch(user_agent, url)

    async def get_sitemaps(self, url: str, client: Optional[httpx.AsyncClient] = None) -> List[str]:
        """Retrieve any declared Sitemap URLs for the host."""
        entry = await self.fetch_and_parse(url, client=client)
        return entry.sitemaps

    async def get_crawl_delay(self, url: str, client: Optional[httpx.AsyncClient] = None) -> Optional[float]:
        """Retrieve declared crawl-delay for the host if present."""
        entry = await self.fetch_and_parse(url, client=client)
        return entry.crawl_delay
