"""Sitemap parser and URL discovery module with XML index support."""

from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

from app.config.logging import get_logger

logger = get_logger("discovery.sitemap")


class SitemapDiscoverer:
    """Discovers URLs by parsing XML sitemaps and recursive sitemap indexes."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def discover(self, sitemap_url: str, client: Optional[httpx.AsyncClient] = None) -> List[str]:
        """Fetch and extract URLs from an XML sitemap or sitemap index."""
        logger.info("discovering_urls_from_sitemap", sitemap_url=sitemap_url)
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
            should_close = True

        discovered_urls: List[str] = []
        try:
            resp = await client.get(sitemap_url)
            if resp.status_code != 200:
                logger.warning("sitemap_fetch_failed", url=sitemap_url, status=resp.status_code)
                return []

            content = resp.text
            soup = BeautifulSoup(content, "xml")

            # Check if this is a sitemapindex pointing to other sitemaps
            sitemaps = soup.find_all("sitemap")
            if sitemaps:
                for sm in sitemaps:
                    loc = sm.find("loc")
                    if loc and loc.text.strip():
                        child_sitemap = loc.text.strip()
                        child_urls = await self.discover(child_sitemap, client=client)
                        discovered_urls.extend(child_urls)
            else:
                # Regular urlset
                urls = soup.find_all("url")
                for u in urls:
                    loc = u.find("loc")
                    if loc and loc.text.strip():
                        discovered_urls.append(loc.text.strip())

        except Exception as exc:
            logger.warning("sitemap_parse_error", url=sitemap_url, error=str(exc))
        finally:
            if should_close:
                await client.aclose()

        logger.info("sitemap_discovery_complete", sitemap_url=sitemap_url, count=len(discovered_urls))
        return discovered_urls
