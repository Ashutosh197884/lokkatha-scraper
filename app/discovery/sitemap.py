"""Sitemap parser and URL discovery module."""

from typing import List
from app.config.logging import get_logger

logger = get_logger("discovery.sitemap")


class SitemapDiscoverer:
    """Discovers URLs by parsing robots.txt sitemaps and XML sitemaps."""

    async def discover(self, sitemap_url: str) -> List[str]:
        """Fetch and extract URLs from an XML sitemap or sitemap index."""
        logger.info("discovering_urls_from_sitemap", sitemap_url=sitemap_url)
        # XML parsing implemented in crawler/discovery phase
        return []
