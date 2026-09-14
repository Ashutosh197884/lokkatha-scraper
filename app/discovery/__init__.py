"""URL discovery engine modules (Search, Sitemap, Internal links)."""

from typing import List, Protocol


class URLDiscoverer(Protocol):
    """Protocol for discovery engines."""
    async def discover(self, source: str) -> List[str]:
        ...
