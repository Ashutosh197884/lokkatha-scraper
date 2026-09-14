"""Search engine discovery interface for finding seed URLs."""

from typing import List
from app.config.logging import get_logger

logger = get_logger("discovery.search")


class SearchDiscoverer:
    """Discovers URLs from search engines via configured search queries."""

    def __init__(self, queries: List[str] | None = None) -> None:
        self.queries = queries or []

    async def discover(self, query: str) -> List[str]:
        """Execute a discovery query and return matching URLs."""
        logger.info("discovering_urls_from_search", query=query)
        # Search engine integration implemented in discovery phase
        return []
