"""Search query builder and multi-source public web discoverer."""

from typing import List
from app.config.logging import get_logger

logger = get_logger("discovery.search")


class SearchDiscoverer:
    """Discovers candidate seed URLs across configured search queries and cultural portals."""

    def __init__(self, queries: List[str] | None = None) -> None:
        self.queries = queries or []

    def build_cultural_queries(self, region: str, genre: str = "folktales") -> List[str]:
        """Generate targeted search queries for regional Indian folklore and TEK."""
        return [
            f"{region} {genre} oral tradition stories",
            f"{region} traditional ecological knowledge water management",
            f"{region} folk tales panchatantra jataka bards",
            f"{region} indigenous myths legends rituals sacred groves",
        ]

    async def discover(self, query: str) -> List[str]:
        """Execute a discovery query returning relevant candidate URLs."""
        logger.info("discovering_urls_from_search", query=query)
        # Curated authoritative seed patterns based on query keywords
        results: List[str] = []
        q_lower = query.lower()
        if "rajasthan" in q_lower:
            results.extend([
                "https://en.wikipedia.org/wiki/Rajasthani_folklore",
                "https://ignca.gov.in/divisions/janapada-sampada/rajasthan",
                "https://sahapedia.org/modules/oral-traditions-rajasthan",
            ])
        elif "bengal" in q_lower or "sundarban" in q_lower:
            results.extend([
                "https://en.wikipedia.org/wiki/Folk_tales_of_Bengal",
                "https://ruralindiaonline.org/en/articles/categories/culture/",
            ])
        else:
            results.append("https://en.wikipedia.org/wiki/Indian_folklore")
        return results
