"""Digital libraries, archives, academic and cultural repository discoverer."""

from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
import httpx

from app.config.logging import get_logger

logger = get_logger("discovery.archive")


class ArchiveItem:
    """Standardized record from an open archive or digital library."""

    def __init__(
        self,
        identifier: str,
        title: str,
        url: str,
        creator: Optional[str] = None,
        year: Optional[str] = None,
        description: str = "",
        collection: str = "",
    ) -> None:
        self.identifier = identifier
        self.title = title
        self.url = url
        self.creator = creator
        self.year = year
        self.description = description
        self.collection = collection


class ArchiveDiscoverer:
    """Discovers folkloric documents across Internet Archive and cultural repositories."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def search_internet_archive(
        self,
        query: str,
        max_results: int = 20,
        client: Optional[httpx.AsyncClient] = None,
    ) -> List[ArchiveItem]:
        """Search Internet Archive open metadata API for folkloric manuscripts and books."""
        logger.info("searching_internet_archive", query=query)
        encoded_query = quote_plus(f"{query} AND (mediatype:texts OR mediatype:audio)")
        api_url = f"https://archive.org/advancedsearch.php?q={encoded_query}&fl[]=identifier,title,creator,year,description,collection&rows={max_results}&output=json"

        should_close = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
            should_close = True

        items: List[ArchiveItem] = []
        try:
            resp = await client.get(api_url)
            if resp.status_code == 200:
                data = resp.json()
                docs = data.get("response", {}).get("docs", [])
                for doc in docs:
                    identifier = doc.get("identifier", "")
                    title = doc.get("title", "Untitled Manuscript")
                    creator = doc.get("creator")
                    year = str(doc.get("year", "")) if doc.get("year") else None
                    desc = doc.get("description", "")
                    colls = doc.get("collection", [])
                    collection_str = colls[0] if isinstance(colls, list) and colls else str(colls)

                    items.append(
                        ArchiveItem(
                            identifier=identifier,
                            title=title,
                            url=f"https://archive.org/details/{identifier}",
                            creator=creator,
                            year=year,
                            description=desc[:300] if desc else "",
                            collection=collection_str,
                        )
                    )
        except Exception as exc:
            logger.warning("archive_search_error", query=query, error=str(exc))
        finally:
            if should_close:
                await client.aclose()

        logger.info("archive_search_complete", query=query, count=len(items))
        return items
