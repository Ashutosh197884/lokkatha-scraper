"""RSS and Atom feed discoverer for news, folklore blogs, and cultural feeds."""

from typing import Any, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

from app.config.logging import get_logger

logger = get_logger("discovery.feed")


class FeedItem:
    """Standardized entry from an RSS or Atom feed."""

    def __init__(
        self,
        url: str,
        title: str = "",
        published_at: Optional[str] = None,
        author: Optional[str] = None,
        summary: str = "",
    ) -> None:
        self.url = url
        self.title = title
        self.published_at = published_at
        self.author = author
        self.summary = summary


class FeedDiscoverer:
    """Discovers article URLs and metadata from RSS 2.0 and Atom XML feeds."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def discover_entries(self, feed_url: str, client: Optional[httpx.AsyncClient] = None) -> List[FeedItem]:
        """Fetch and parse feed into structured FeedItem entries."""
        logger.info("discovering_feed_entries", feed_url=feed_url)
        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
            should_close = True

        entries: List[FeedItem] = []
        try:
            resp = await client.get(feed_url)
            if resp.status_code != 200:
                logger.warning("feed_fetch_failed", url=feed_url, status=resp.status_code)
                return []

            soup = BeautifulSoup(resp.text, "xml")

            # Check RSS 2.0 <item>
            items = soup.find_all("item")
            if items:
                for it in items:
                    link_tag = it.find("link")
                    title_tag = it.find("title")
                    pub_date_tag = it.find("pubDate") or it.find("dc:date")
                    author_tag = it.find("author") or it.find("dc:creator")
                    desc_tag = it.find("description")

                    url = link_tag.text.strip() if link_tag and link_tag.text else ""
                    if not url and link_tag and link_tag.get("href"):
                        url = link_tag["href"].strip()

                    if url:
                        entries.append(
                            FeedItem(
                                url=url,
                                title=title_tag.text.strip() if title_tag else "",
                                published_at=pub_date_tag.text.strip() if pub_date_tag else None,
                                author=author_tag.text.strip() if author_tag else None,
                                summary=desc_tag.text.strip() if desc_tag else "",
                            )
                        )

            # Check Atom <entry>
            atom_entries = soup.find_all("entry")
            if atom_entries:
                for entry in atom_entries:
                    link_tag = entry.find("link")
                    title_tag = entry.find("title")
                    pub_tag = entry.find("published") or entry.find("updated")
                    author_tag = entry.find("author")
                    summary_tag = entry.find("summary") or entry.find("content")

                    url = ""
                    if link_tag:
                        url = link_tag.get("href", "").strip() or link_tag.text.strip()

                    author_name = None
                    if author_tag:
                        name_tag = author_tag.find("name")
                        author_name = name_tag.text.strip() if name_tag else author_tag.text.strip()

                    if url:
                        entries.append(
                            FeedItem(
                                url=url,
                                title=title_tag.text.strip() if title_tag else "",
                                published_at=pub_tag.text.strip() if pub_tag else None,
                                author=author_name,
                                summary=summary_tag.text.strip() if summary_tag else "",
                            )
                        )

        except Exception as exc:
            logger.warning("feed_parse_error", url=feed_url, error=str(exc))
        finally:
            if should_close:
                await client.aclose()

        logger.info("feed_discovery_complete", feed_url=feed_url, count=len(entries))
        return entries

    async def discover_urls(self, feed_url: str, client: Optional[httpx.AsyncClient] = None) -> List[str]:
        """Convenience method to return URLs only."""
        entries = await self.discover_entries(feed_url, client=client)
        return [e.url for e in entries]
